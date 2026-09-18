"""aeoi crs validate: XML files from any tool, checked like the portal would."""

import datetime as dt
from pathlib import Path

from aeoi.crs import build, read_xml, validate, xsd
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


def test_wegleitung_header_variant_is_checked_as_30_and_noted(tmp_path):
    """The header the Wegleitung 5.3.1 shows (v2 declaration, version 3.0) is a legitimate variant
    the builder can write; the validator checks the content as 3.0 and notes the open question."""
    built = build.build(sample_message(), "3.0", header="wegleitung")
    assert built.header == "wegleitung" and build.is_wegleitung_header(built.xml)
    assert 'xmlns:crs="urn:oecd:ties:crs:v2"' in built.xml and 'version="3.0"' in built.xml
    assert "<crs:SelfCert>" in built.xml  # 3.0 content
    canonical = build.canonical_xml(built.xml)
    assert 'xmlns:crs="urn:oecd:ties:crs:v3"' in canonical and xsd.validate(canonical, "3.0") == []
    assert xsd.validate(built.xml, "3.0") != []  # the variant itself is not schema-valid
    rep = validate.validate_file(_write(tmp_path, built.xml, "prod.xml"), today=TODAY)
    assert rep.ok and rep.version == "3.0"
    assert [p.message for p in rep.infos if "Wegleitung 5.3.1" in p.message]
    # the default header is the OECD namespace and gets no note
    plain = validate.validate_file(
        _write(tmp_path, build.build(sample_message(), "3.0").xml, "prod2.xml"), today=TODAY
    )
    assert plain.ok and not [p for p in plain.infos if "Wegleitung 5.3.1" in p.message]


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


def test_80001_compares_with_the_message_ref_id_year(tmp_path):
    """MessageRefId CH2017CH..., ReportingPeriod 2018-12-31: 98006 allows year+1, and the DocRefIds
    carry 2017 like the MessageRefId - no 80001 (ESTV: 'Das Berichtsjahr muss dabei dem Wert aus
    der MessageRefId entsprechen')."""
    msg = sample_message(year=2017)
    xml = build.build(msg, "3.0", test=True).xml.replace("2017-12-31", "2018-12-31")
    rep = validate.validate_file(_write(tmp_path, xml), today=TODAY)
    assert "80001" not in {p.rule for p in rep.problems}, rep.render()
    assert "98006" not in {p.rule for p in rep.problems}  # year + 1 is within the ESTV formula
    assert any("year after the MessageRefId year" in p.message for p in rep.infos)
    xml = build.build(msg, "3.0", test=True).xml.replace("2017-12-31", "2019-12-31")
    rep = validate.validate_file(_write(tmp_path, xml), today=TODAY)
    assert "98006" in {p.rule for p in rep.problems}
    assert "80001" not in {p.rule for p in rep.problems}


def test_forbidden_character_is_reported_once(tmp_path):
    xml = build.build(sample_message(), "3.0", test=True).xml.replace(
        "Beispiel AG", "Beispiel # AG"
    )
    rep = validate.validate_file(_write(tmp_path, xml), today=TODAY)
    assert [p.rule for p in rep.problems] == ["50005"], rep.render()


def test_non_schema_file_has_no_traceback(tmp_path):
    xml = build.build(sample_message(), "3.0", test=True).xml.replace(
        "<crs:CrsBody>", "<crs:CrsBody><crs:X/>"
    )
    rep = validate.validate_file(_write(tmp_path, xml), today=TODAY)
    assert rep.problems and all(p.rule == "50007" for p in rep.problems)
    assert any("content checks skipped" in i.message for i in rep.infos)
    assert not any("__init__" in p.message for p in rep.problems)
