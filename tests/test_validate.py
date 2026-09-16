"""aeoi crs validate: XML files from any tool, checked like the portal would."""

import datetime as dt
from pathlib import Path

from aeoi.crs import build, read_xml, validate
from aeoi.crs.example import sample_message

ROOT = Path(__file__).resolve().parents[1]
TODAY = dt.date(2027, 3, 1)


def _write(tmp_path, xml: str, name="Test-report.xml") -> Path:
    p = tmp_path / name
    p.write_text(xml, encoding="utf-8")
    return p


def test_built_files_validate_clean(tmp_path):
    for version in ("2.0", "3.0"):
        xml = build.build(sample_message(), version, test=True).xml
        rep = validate.validate_file(_write(tmp_path, xml), today=TODAY)
        assert rep.ok, rep.render()
        assert rep.version == version


def test_estv_annex_examples_validate_as_productive_2_0(tmp_path):
    for path in sorted((ROOT / "tests" / "corpus" / "estv_v2").glob("*.xml")):
        rep = validate.validate_file(path, test=False, today=dt.date(2018, 6, 1))
        # the examples use 2017 data; partner-state and content rules apply to them too
        errors = [p for p in rep.problems if p.rule not in ("98200", "98201", "98202")]
        assert not errors, (path.name, rep.render())


def test_round_trip_through_read_xml():
    msg = sample_message()
    parsed = read_xml.parse(build.build(msg, "3.0").xml)
    assert parsed.version == "3.0" and parsed.message.reporting_year == 2026
    assert parsed.message.reporting_fi.estv_id == msg.reporting_fi.estv_id
    assert [a.account_number for a in parsed.message.accounts] == [
        a.account_number for a in msg.accounts
    ]
    got = parsed.message.accounts[1]
    assert got.holder_organisation.name == "Holding Trust Ltd"
    assert got.controlling_persons[0].ctrlg_person_types == ["CRS804", "CRS807"]
    assert got.self_cert == "CRS902" and got.equity_interest_types == ["CRS401"]
    assert parsed.account_specs[0].doc_type_indic == "OECD1"


def test_structural_rules_are_reported(tmp_path):
    xml = build.build(sample_message(), "3.0", test=True).xml
    broken = xml.replace(
        "<crs:ReceivingCountry>CH</crs:ReceivingCountry>",
        "<crs:ReceivingCountry>DE</crs:ReceivingCountry>",
    ).replace(
        "<stf:DocTypeIndic>OECD11</stf:DocTypeIndic>",
        "<stf:DocTypeIndic>OECD1</stf:DocTypeIndic>",
        1,
    )
    rep = validate.validate_file(_write(tmp_path, broken), today=TODAY)
    rules = {p.rule for p in rep.problems}
    assert {"50012", "50011"} <= rules, rep.render()


def test_wegleitung_header_namespace_is_explained(tmp_path):
    xml = build.build(sample_message(), "3.0").xml.replace(
        "urn:oecd:ties:crs:v3", "urn:oecd:ties:crs:v2"
    )
    rep = validate.validate_file(_write(tmp_path, xml, "prod.xml"), today=TODAY)
    assert [p.rule for p in rep.problems] == ["98000"]
    assert "open question 1" in rep.problems[0].message


def test_correction_file_rules(tmp_path):
    from aeoi.crs.build import FiPlan, RecordPlan

    msg = sample_message()
    plans = [
        RecordPlan("A1", "CH2026CHc1", "OECD2", "CH2026CHorig1"),
        RecordPlan("A2", "CH2026CHc2", "OECD3", "CH2026CHorig1"),  # same target twice
    ]
    msg.message_type_indic = "CRS702"
    xml = build.build(msg, "3.0", records=plans, fi_plan=FiPlan("CH2026CHfi", resend=True)).xml
    rep = validate.validate_file(_write(tmp_path, xml, "corr.xml"), today=TODAY)
    assert "80011" in {p.rule for p in rep.problems}
    # a CRS701 message with OECD2 records
    msg.message_type_indic = "CRS701"
    xml = build.build(msg, "3.0", records=plans[:1] + [RecordPlan("A2", "CH2026CHn2", "OECD1")]).xml
    rep = validate.validate_file(_write(tmp_path, xml, "mixed.xml"), today=TODAY)
    assert "80010" in {p.rule for p in rep.problems}


def test_content_rules_reach_the_validator(tmp_path):
    msg = sample_message()
    msg.accounts[0].holder_person.residence_countries = ["US"]
    xml = build.build(msg, "3.0", test=True).xml
    rep = validate.validate_file(_write(tmp_path, xml), today=TODAY)
    assert "98200" in {p.rule for p in rep.problems}


def test_signed_or_malformed_files(tmp_path):
    rep = validate.validate_file(_write(tmp_path, "<not xml", "x.xml"))
    assert not rep.ok and rep.problems[0].rule == "50007"
