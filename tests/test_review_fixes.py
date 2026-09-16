"""Regression tests for the week-2 review: UID optional, TDT, character set, CRS702, codes, joint accounts."""

import datetime as dt

from lxml import etree

from aeoi.crs import build, flat, model, template, xsd
from aeoi.crs.example import sample_message

TODAY = dt.date(2027, 3, 1)
NS = {"crs": "urn:oecd:ties:crs:v3"}


def _rules(msg, version="3.0"):
    return {(p.where, p.rule) for p in model.check_message(msg, version, today=TODAY).problems}


def _errors(msg, version="3.0"):
    return [p for p in model.check_message(msg, version, today=TODAY).problems if p.rule != "info"]


def test_uid_is_optional_and_in_is_omitted_when_absent():
    msg = sample_message()
    msg.reporting_fi.uid = None
    assert not _errors(msg)
    root = etree.fromstring(build.build(msg, "3.0").xml.encode())
    fi = root.find("crs:CrsBody/crs:ReportingFI", NS)
    assert fi.find("crs:IN", NS) is None
    assert not xsd.validate(build.build(msg, "3.0").xml, "3.0")
    msg.reporting_fi.uid = "123"
    assert ("ReportingFI.uid", "70015") in _rules(msg)


def test_trustee_documented_trust_prefix():
    msg = sample_message()
    msg.reporting_fi.name = "Family Trust"
    msg.reporting_fi.trustee_documented_trust = True
    assert not _errors(msg)
    root = etree.fromstring(build.build(msg, "3.0").xml.encode())
    assert (
        root.findtext("crs:CrsBody/crs:ReportingFI/crs:Name", namespaces=NS) == "TDT=Family Trust"
    )
    # written by hand without the flag: refused
    msg.reporting_fi.trustee_documented_trust = False
    msg.reporting_fi.name = "TDT=Family Trust"
    assert ("ReportingFI.name", "5.3.4") in _rules(msg)


def test_character_set_is_enforced_on_text_fields():
    msg = sample_message()
    msg.accounts[0].holder_person.last_name = "Müller « Söhne » €"
    msg.accounts[0].holder_person.address.street = "Rue -- test /* x"
    msg.reporting_fi.name = "Beispiel AG #1"
    msg.accounts[1].holder_organisation.ins[0].value = "FR<1>"
    msg.accounts[0].account_number = "CH93 $"
    rules = _rules(msg)
    for where in (
        "Accounts[key=A1].holder.last_name",
        "Accounts[key=A1].holder.address.street",
        "ReportingFI.name",
        "Accounts[key=A2].holder.ins[0]",
        "Accounts[key=A1].account_number",
    ):
        assert (where, "50005") in rules, where


def test_crs702_is_refused_until_corrections_exist():
    msg = sample_message()
    msg.message_type_indic = "CRS702"
    assert ("Message.message_type_indic", "80010") in _rules(msg)


def test_message_header_codes():
    msg = sample_message()
    msg.message_type_indic = "XYZ"
    assert ("Message.message_type_indic", "98004") in _rules(msg)
    msg = sample_message()
    msg.message_type_indic = "CRS703"
    assert ("Message.accounts", "98005") in _rules(msg)
    msg = sample_message()
    msg.accounts = []
    assert ("Message.accounts", "60015") in _rules(msg)


def test_estv_id_shape_is_only_a_warning():
    msg = sample_message()
    msg.reporting_fi.estv_id = "CHE-99"
    problems = model.check_message(msg, "3.0", today=TODAY).problems
    assert [p.rule for p in problems if p.where == "ReportingFI.estv_id"] == ["info"]
    msg.reporting_fi.estv_id = ""
    assert ("ReportingFI.estv_id", "98001") in _rules(msg)


def test_joint_account_rows_need_a_consistent_number():
    msg = sample_message()
    second = msg.accounts[0].model_copy(deep=True)
    second.key = "A1b"
    second.holder_person.first_name = "Bruno"
    msg.accounts.append(second)
    assert any(r == "3.0" and w.startswith("Accounts[account_number=") for w, r in _rules(msg))
    msg.accounts[0].joint_account_number = 2
    second.joint_account_number = 2
    assert not _errors(msg)
    assert not _errors(msg, "2.0")  # no JointAccount element in 2.0, no rule


def test_duplicate_doc_ref_id_is_reported():
    msg = sample_message()
    msg.accounts[0].doc_ref_id = msg.accounts[1].doc_ref_id = "CH2026CHsame"
    assert ("Accounts[doc_ref_id=CH2026CHsame]", "80000") in _rules(msg)


def test_contact_is_not_written():
    assert "<crs:Contact" not in build.build(sample_message(), "3.0").xml


def test_template_round_trip_keeps_uid_and_tdt(tmp_path):
    msg = sample_message()
    msg.reporting_fi.uid = None
    msg.reporting_fi.trustee_documented_trust = True
    path = tmp_path / "tdt.xlsx"
    template.write_message(msg, path)
    result = flat.read(path)
    assert result.ok, [str(p) for p in result.problems]
    assert result.message.reporting_fi.uid is None
    assert result.message.reporting_fi.trustee_documented_trust is True


def test_xsd_validate_reports_errors():
    xml = build.build(sample_message(), "3.0").xml.replace(
        "<crs:DDProcedure>CRS1202</crs:DDProcedure>", ""
    )
    errors = xsd.validate(xml, "3.0")
    assert errors and any("DDProcedure" in e for e in errors)
    assert not xsd.validate(build.build(sample_message(), "3.0").xml, "3.0")
