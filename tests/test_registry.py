"""Submission registry and correction workflow, following the sequences of Wegleitung Ziffer 6."""

from decimal import Decimal

import pytest
from lxml import etree

from aeoi.crs import submit, xsd
from aeoi.crs.example import sample_message
from aeoi.estv import status
from aeoi.registry import Registry, RegistryError

NS = {"crs": "urn:oecd:ties:crs:v3", "stf": "urn:oecd:ties:crsstf:v5"}


@pytest.fixture
def reg(tmp_path):
    with Registry(tmp_path / "reg.sqlite") as r:
        yield r


def _doc_specs(xml: str) -> list[tuple[str, str, str | None]]:
    """(DocTypeIndic, DocRefId, CorrDocRefId) for every DocSpec in document order."""
    root = etree.fromstring(xml.encode())
    out = []
    for spec in root.iter("{urn:oecd:ties:crs:v3}DocSpec"):
        out.append(
            (
                spec.findtext("stf:DocTypeIndic", namespaces=NS),
                spec.findtext("stf:DocRefId", namespaces=NS),
                spec.findtext("stf:CorrDocRefId", namespaces=NS),
            )
        )
    return out


def _accept(reg, message_ref_id):
    submit.record_outcome(
        reg, message_ref_id, status.Outcome(True, message_ref_id, []), source="test"
    )


def test_new_message_registers_fresh_identifiers(reg):
    msg = sample_message()
    result = submit.build_new(msg, "3.0", reg)
    specs = _doc_specs(result.xml)
    assert specs[0][0] == "OECD1" and specs[0][2] is None  # ReportingFI, first time
    assert [s[0] for s in specs[1:]] == ["OECD1", "OECD1"]
    assert reg.message(result.message_ref_id)["status"] == "built"
    assert reg.record(result.doc_ref_ids["A1"]).doc_type_indic == "OECD1"
    assert not xsd.validate(result.xml, "3.0")


def test_second_new_message_resends_the_fi_and_refuses_duplicate_accounts(reg):
    first = submit.build_new(sample_message(), "3.0", reg)
    _accept(reg, first.message_ref_id)
    # the same accounts again: refused (6.1: only records not sent before)
    with pytest.raises(RegistryError, match="already has a valid record"):
        submit.build_new(sample_message(), "3.0", reg)
    # a further account in a new message: FI resent as OECD0 with the same DocRefId (6.4.6)
    more = sample_message()
    more.accounts = [more.accounts[0].model_copy(update={"key": "A3", "account_number": "NANUM",
                                                         "account_number_type": None})]  # fmt: skip
    second = submit.build_new(more, "3.0", reg)
    specs = _doc_specs(second.xml)
    assert specs[0] == ("OECD0", first.reporting_fi_doc_ref_id, None)
    assert specs[1][0] == "OECD1"


def test_correction_chain_6_4_1(reg):
    """Two successive corrections of the same AccountReport: CorrDocRefId always points to the
    directly preceding link; the FI is resent as OECD0; the unchanged account is left out."""
    original = sample_message()
    first = submit.build_new(original, "3.0", reg)
    _accept(reg, first.message_ref_id)

    fixed = sample_message()
    fixed.accounts[0].balance = Decimal("130000.00")
    result, plan = submit.build_correction(fixed, "3.0", reg)
    assert plan.skipped_unchanged == ["A2"]
    specs = _doc_specs(result.xml)
    assert specs[0] == ("OECD0", first.reporting_fi_doc_ref_id, None)
    assert len(specs) == 2 and specs[1][0] == "OECD2"
    assert specs[1][2] == first.doc_ref_ids["A1"]
    assert "CRS702" in result.xml and not xsd.validate(result.xml, "3.0")
    first_corr = specs[1][1]
    _accept(reg, result.message_ref_id)

    fixed.accounts[0].balance = Decimal("131000.00")
    result2, _ = submit.build_correction(fixed, "3.0", reg)
    specs2 = _doc_specs(result2.xml)
    assert specs2[1][2] == first_corr  # the previous correction, not the initial record
    assert reg.record(first.doc_ref_ids["A1"]).superseded_by == first_corr
    assert reg.record(first_corr).superseded_by == specs2[1][1]


def test_nothing_changed_builds_nothing(reg):
    first = submit.build_new(sample_message(), "3.0", reg)
    _accept(reg, first.message_ref_id)
    result, plan = submit.build_correction(sample_message(), "3.0", reg)
    assert result is None and sorted(plan.skipped_unchanged) == ["A1", "A2"]


def test_deletion_6_4_5_and_readding_6_4_7(reg):
    first = submit.build_new(sample_message(), "3.0", reg)
    _accept(reg, first.message_ref_id)
    result, plan = submit.build_correction(sample_message(), "3.0", reg, cancel=["A2"])
    specs = _doc_specs(result.xml)
    assert len(specs) == 2 and specs[1][0] == "OECD3" and specs[1][2] == first.doc_ref_ids["A2"]
    # the deletion carries the ResCountryCodes of the deleted record (98204)
    root = etree.fromstring(result.xml.encode())
    codes = {e.text for e in root.iter("{urn:oecd:ties:crs:v3}ResCountryCode")}
    assert "FR" in codes
    _accept(reg, result.message_ref_id)
    # a deleted record cannot be corrected (98103)
    changed = sample_message()
    changed.accounts[1].balance = Decimal(5)
    with pytest.raises(RegistryError, match="98103"):
        submit.build_correction(changed, "3.0", reg)
    # ... it is sent again as a new record with a new DocRefId (6.4.7)
    again = sample_message()
    again.accounts = [again.accounts[1]]
    third = submit.build_new(again, "3.0", reg)
    assert third.doc_ref_ids["A2"] != first.doc_ref_ids["A2"]
    assert _doc_specs(third.xml)[1][0] == "OECD1"


def test_deletion_without_the_row_uses_stored_content(reg):
    first = submit.build_new(sample_message(), "3.0", reg)
    _accept(reg, first.message_ref_id)
    only_a1 = sample_message()
    only_a1.accounts = [only_a1.accounts[0]]
    result, plan = submit.build_correction(only_a1, "3.0", reg, cancel=["A2"])
    specs = _doc_specs(result.xml)
    assert [s[0] for s in specs[1:]] == ["OECD3"]
    assert "Holding Trust Ltd" in result.xml


def test_new_account_in_a_correction_is_refused(reg):
    first = submit.build_new(sample_message(), "3.0", reg)
    _accept(reg, first.message_ref_id)
    msg = sample_message()
    msg.accounts[0].key = "NEW"
    with pytest.raises(RegistryError, match="new accounts go into a new message"):
        submit.build_correction(msg, "3.0", reg)


def test_correction_needs_a_recorded_outcome(reg):
    submit.build_new(sample_message(), "3.0", reg)
    changed = sample_message()
    changed.accounts[0].balance = Decimal(1)
    with pytest.raises(RegistryError, match="no recorded outcome"):
        submit.build_correction(changed, "3.0", reg)


def test_rejected_correction_frees_the_chain(reg):
    first = submit.build_new(sample_message(), "3.0", reg)
    _accept(reg, first.message_ref_id)
    changed = sample_message()
    changed.accounts[0].balance = Decimal(1)
    corr, _ = submit.build_correction(changed, "3.0", reg)
    outcome = status.parse_text("Fehlerbericht\n60002 negativ " + corr.doc_ref_ids["A1"])
    submit.record_outcome(reg, corr.message_ref_id, outcome, source="text")
    assert reg.message(corr.message_ref_id)["status"] == "rejected"
    assert reg.record(first.doc_ref_ids["A1"]).superseded_by is None
    findings = reg.conn.execute("SELECT code, doc_ref_id FROM findings").fetchall()
    assert [tuple(f) for f in findings] == [("60002", corr.doc_ref_ids["A1"])]
    # the next correction points to the original record again
    corr2, _ = submit.build_correction(changed, "3.0", reg)
    assert _doc_specs(corr2.xml)[1][2] == first.doc_ref_ids["A1"]


def test_nil_report_rules_6_4_8(reg):
    nil = sample_message()
    nil.accounts = []
    nil.message_type_indic = "CRS703"
    first = submit.build_new(nil, "3.0", reg)
    assert "CRS703" in first.xml
    _accept(reg, first.message_ref_id)
    # data after a nil report is a normal new message; nil after data is refused (98009)
    data = submit.build_new(sample_message(), "3.0", reg)
    _accept(reg, data.message_ref_id)
    with pytest.raises(RegistryError, match="98009"):
        submit.build_new(nil, "3.0", reg)


def test_identifiers_are_never_reused(reg):
    first = submit.build_new(sample_message(), "3.0", reg)
    again = sample_message()
    again.message_ref_id = first.message_ref_id
    with pytest.raises(RegistryError, match="50009"):
        submit.build_new(again, "3.0", reg)
    again = sample_message()
    again.accounts = [
        again.accounts[0].model_copy(update={"key": "X", "doc_ref_id": first.doc_ref_ids["A1"]})
    ]
    with pytest.raises(RegistryError, match="80000"):
        submit.build_new(again, "3.0", reg)


def test_test_and_productive_chains_are_separate(reg):
    prod = submit.build_new(sample_message(), "3.0", reg, test=False)
    _accept(reg, prod.message_ref_id)
    test = submit.build_new(sample_message(), "3.0", reg, test=True)
    specs = _doc_specs(test.xml)
    assert specs[0][0] == "OECD11" and specs[0][1] != prod.reporting_fi_doc_ref_id
    assert reg.summary().count("TEST") == 1


def test_crs702_from_the_workbook_alone_is_still_refused():
    from aeoi.crs import model

    msg = sample_message()
    msg.message_type_indic = "CRS702"
    rules = {p.rule for p in model.check_message(msg, "3.0").problems}
    assert "80010" in rules
