"""Domain -> XML: valid against the OECD XSD for both versions, ESTV header rules respected."""

import datetime as dt
from pathlib import Path

import pytest
import xmlschema
from lxml import etree

from aeoi.crs import build, model
from aeoi.crs.example import sample_message
from aeoi.estv import ids

ROOT = Path(__file__).resolve().parents[1]
TODAY = dt.date(2027, 3, 1)


@pytest.fixture(scope="module")
def schemas():
    return {
        "2.0": xmlschema.XMLSchema(ROOT / "schemas" / "crs_v2.0" / "CrsXML_v2.0.xsd"),
        "3.0": xmlschema.XMLSchema(ROOT / "schemas" / "crs_v3.0" / "CrsXML_v3.0.xsd"),
    }


@pytest.mark.parametrize("version", ["2.0", "3.0"])
def test_sample_has_no_problems(version):
    rep = model.check_message(sample_message(), version, today=TODAY)
    problems = [p for p in rep.problems if p.rule != "info"]
    assert not problems, problems


@pytest.mark.parametrize("version", ["2.0", "3.0"])
def test_built_xml_is_schema_valid(version, schemas):
    result = build.build(sample_message(), version, test=True)
    errors = [e.reason for e in schemas[version].iter_errors(result.xml)]
    assert not errors, errors
    assert result.xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "&#" not in result.xml and "Zürich" in result.xml


def test_v3_uses_the_oecd_namespace_only():
    xml = build.build(sample_message(), "3.0").xml
    assert 'xmlns:crs="urn:oecd:ties:crs:v3"' in xml
    assert "urn:oecd:ties:crs:v2" not in xml
    assert 'version="3.0"' in xml


def test_v2_document_has_no_v3_elements():
    xml = build.build(sample_message(), "2.0").xml
    for tag in ("SelfCert", "DDProcedure", "AccountType", "JointAccount", "EquityInterestType"):
        assert f"<crs:{tag}" not in xml
    assert 'version="2.0"' in xml and 'xmlns:crs="urn:oecd:ties:crs:v2"' in xml


def test_header_follows_wegleitung_5_3_2():
    msg = sample_message(2026)
    result = build.build(msg, "3.0", now=dt.datetime(2027, 5, 1, 9, 30, tzinfo=dt.UTC))
    root = etree.fromstring(result.xml.encode("utf-8"))
    ns = {"crs": "urn:oecd:ties:crs:v3", "stf": "urn:oecd:ties:crsstf:v5"}
    get = lambda p: root.findtext(p, namespaces=ns)
    assert get("crs:MessageSpec/crs:SendingCompanyIN") == "052.0000.0000"
    assert get("crs:MessageSpec/crs:TransmittingCountry") == "CH"
    assert get("crs:MessageSpec/crs:ReceivingCountry") == "CH"
    assert get("crs:MessageSpec/crs:MessageType") == "CRS"
    assert get("crs:MessageSpec/crs:MessageTypeIndic") == "CRS701"
    assert get("crs:MessageSpec/crs:ReportingPeriod") == "2026-12-31"
    assert get("crs:MessageSpec/crs:Timestamp") == "2027-05-01T09:30:00Z"
    assert ids.check_message_ref_id(result.message_ref_id).ok
    assert result.message_ref_id.startswith("CH2026CH")
    for ref in result.doc_ref_ids.values():
        assert ids.check_doc_ref_id(ref, message_year=2026).ok
    fi = root.find("crs:CrsBody/crs:ReportingFI", ns)
    assert fi.findtext("crs:IN", namespaces=ns) == "CHE-123.456.789"
    assert fi.find("crs:IN", ns).get("issuedBy") == "CH"
    assert fi.findtext("crs:DocSpec/stf:DocTypeIndic", namespaces=ns) == "OECD1"


def test_test_flag_uses_test_doc_type_indics():
    xml = build.build(sample_message(), "3.0", test=True).xml
    assert "OECD11" in xml and ">OECD1<" not in xml


def test_element_order_in_v3_matches_schema_sequences():
    root = etree.fromstring(build.build(sample_message(), "3.0").xml.encode("utf-8"))
    ns = "urn:oecd:ties:crs:v3"
    local = lambda el: etree.QName(el).localname
    report = root.find(f".//{{{ns}}}AccountReport[2]")
    names = [local(c) for c in report]
    assert names == [
        "DocSpec", "AccountNumber", "AccountHolder", "ControllingPerson", "AccountBalance",
        "Payment", "DDProcedure", "AccountType",
    ]  # fmt: skip
    holder = report.find(f"{{{ns}}}AccountHolder")
    assert [local(c) for c in holder] == [
        "EquityInterestType",
        "SelfCert",
        "Organisation",
        "AcctHolderType",
    ]
    cp = report.find(f"{{{ns}}}ControllingPerson")
    assert [local(c) for c in cp] == [
        "Individual",
        "CtrlgPersonType",
        "CtrlgPersonType",
        "SelfCert",
    ]


def test_given_doc_ref_ids_are_kept():
    msg = sample_message()
    msg.accounts[0].doc_ref_id = "CH2026CHfixed-ref-1"
    result = build.build(msg, "3.0")
    assert result.doc_ref_ids["A1"] == "CH2026CHfixed-ref-1"
    assert "CH2026CHfixed-ref-1" in result.xml


def test_nil_report():
    msg = sample_message()
    msg.accounts = []
    msg.message_type_indic = "CRS703"
    assert model.check_message(msg, "3.0", today=TODAY).ok
    xml = build.build(msg, "3.0").xml
    assert "CRS703" in xml and "AccountReport" not in xml


# --- talking errors --------------------------------------------------------------------------


def test_missing_v3_fields_are_reported_with_location():
    msg = sample_message()
    msg.accounts[0].self_cert = None
    msg.accounts[0].dd_procedure = None
    msg.accounts[0].account_type = None
    msg.accounts[1].controlling_persons[0].ctrlg_person_types = []
    msg.accounts[1].controlling_persons[0].self_cert = None
    rep = model.check_message(msg, "3.0", today=TODAY)
    where = {p.where for p in rep.problems}
    assert {
        "Accounts[key=A1].self_cert",
        "Accounts[key=A1].dd_procedure",
        "Accounts[key=A1].account_type",
        "Accounts[key=A2].controlling_persons[0].ctrlg_person_types",
        "Accounts[key=A2].controlling_persons[0].self_cert",
    } <= where
    # the same message is fine for 2.0
    assert not [
        p for p in model.check_message(msg, "2.0", today=TODAY).problems if p.rule != "info"
    ]


@pytest.mark.parametrize(
    "mutate,rule",
    [
        (lambda m: setattr(m.accounts[0], "balance", m.accounts[0].balance * -1), "60002"),
        (lambda m: setattr(m.accounts[0], "closed", True), "60003"),
        (lambda m: setattr(m.accounts[0].holder_person, "name_type", "OECD201"), "60004"),
        (
            lambda m: setattr(m.accounts[1].holder_organisation, "acct_holder_type", "CRS102"),
            "60005",
        ),
        (lambda m: setattr(m.accounts[1], "controlling_persons", []), "60006"),
        (
            lambda m: setattr(m.accounts[0].holder_person, "birth_date", dt.date(1899, 12, 31)),
            "60014",
        ),
        (lambda m: setattr(m.accounts[0], "account_type", "CRS1102"), "60018"),
        (lambda m: setattr(m.accounts[1], "account_type", "CRS1101"), "60019"),
        (lambda m: setattr(m.accounts[0].payments[0], "payment_type", "CRS501"), "60021"),
        (lambda m: setattr(m.accounts[0], "undocumented", True), "98203"),
        (lambda m: setattr(m.reporting_fi, "uid", "123"), "70015"),
        (lambda m: setattr(m.reporting_fi, "estv_id", ""), "98001"),
    ],
)
def test_estv_rules_are_detected(mutate, rule):
    msg = sample_message()
    mutate(msg)
    rep = model.check_message(msg, "3.0", today=TODAY)
    assert rule in {p.rule for p in rep.problems}, rep.problems


def test_transitional_values_are_accepted_in_v3_only():
    msg = sample_message()
    msg.accounts[0].self_cert = "CRS900"
    msg.accounts[0].account_type = "CRS1100"
    msg.accounts[0].dd_procedure = "CRS1200"
    rep = model.check_message(msg, "3.0", today=TODAY)
    assert not [p for p in rep.problems if p.rule != "info"], rep.problems
    xml = build.build(msg, "3.0").xml
    assert "CRS900" in xml and "CRS1100" in xml and "CRS1200" in xml
