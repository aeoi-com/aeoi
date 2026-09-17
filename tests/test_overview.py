"""Titles per rule code and the structured report the browser page renders."""

from __future__ import annotations

import json
import re
from pathlib import Path

from aeoi.crs import build, check, overview, template, validate
from aeoi.crs.example import sample_message
from aeoi.estv import status, titles

SRC = Path(__file__).resolve().parents[1] / "src" / "aeoi"


def test_every_catalogue_code_has_titles_in_all_languages():
    data = titles.titles()
    for code in status.catalogue():
        assert code in data, f"no title for catalogue code {code}"
    for code, entry in data.items():
        for lang in titles.LANGUAGES:
            assert entry["title"].get(lang), (code, lang)
            assert entry["fix"].get(lang), (code, lang)
            assert len(entry["title"][lang]) <= 90, (code, lang)


def test_every_rule_code_emitted_by_the_engine_has_a_title():
    emitted: set[str] = set()
    for f in ("crs/model.py", "crs/validate.py", "crs/flat.py", "crs/check.py", "crs/submit.py"):
        text = (SRC / f).read_text(encoding="utf-8")
        emitted |= set(re.findall(r'"(\d{5})"', text))
    data = titles.titles()
    missing = sorted(c for c in emitted if c not in data)
    assert not missing, missing
    assert titles.rule_title("aeoi:joint", "fr").startswith("Règle")
    assert titles.rule_title("99999", "it") == "99999"  # unknown: the code itself
    assert titles.rule_title("50005", "xx") == titles.rule_title("50005", "de")  # fallback


def test_locate_maps_model_paths_and_xpaths():
    assert overview.locate("Accounts[key=A1].self_cert") == {
        "scope": "account",
        "ref": "A1",
        "field": "self_cert",
    }
    loc = overview.locate(
        "/crs:CRS_OECD/crs:CrsBody/crs:ReportingGroup/crs:AccountReport[2]/crs:AccountNumber"
    )
    assert loc["scope"] == "account" and loc["ref"] == "2" and loc["field"] == "AccountNumber"
    assert overview.locate("/crs:CRS_OECD/crs:CrsBody/crs:ReportingFI/crs:Name")["scope"] == "fi"
    assert overview.locate("MessageSpec/MessageRefId")["scope"] == "header"
    assert (
        overview.locate("Accounts[key=A2].controlling_persons[0].self_cert")["controlling_person"]
        == 0
    )


def test_report_dict_for_xml(tmp_path):
    xml = build.build(sample_message(), "3.0", test=True).xml
    good = tmp_path / "Test-good.xml"
    good.write_text(xml, encoding="utf-8")
    d = overview.report_dict(validate.validate_file(good), "it")
    assert d["kind"] == "xml" and d["ok"] and d["version"] == "3.0"
    assert d["counts"] == {"error": 0, "input": 0, "info": 0}
    ov = d["overview"]
    assert ov["fi_name"] == "Beispiel AG" and ov["year"] == 2026 and ov["accounts"] == 2
    assert ov["individuals"] + ov["organisations"] == 2
    assert sum(r["count"] for r in ov["residence"]) >= 2
    json.dumps(d)  # JSON-ready

    bad = tmp_path / "Test-bad.xml"
    bad.write_text(xml.replace("Beispiel AG", "Beispiel # AG"), encoding="utf-8")
    d = overview.report_dict(validate.validate_file(bad), "it")
    assert not d["ok"] and d["counts"]["error"] == 1
    p = d["problems"][0]
    assert p["rule"] == "50005" and p["title"] == "Carattere non ammesso"
    assert p["scope"] == "fi" and p["field"] == "Name" and p["official"].startswith("Datenelemente")
    assert "#" in p["fix"] and p["origin"] == "estv"
    assert d["text"].startswith("NOT OK") and d["headline"] == d["text"].split("\n")[0]


def test_report_dict_for_workbook(tmp_path):
    path = tmp_path / "example.xlsx"
    template.write_message(sample_message(), path)
    d = overview.report_dict(check.check_workbook(path, "3.0"), "fr")
    assert d["kind"] == "workbook" and d["ok"] and d["overview"]["accounts"] == 2
    assert d["headline"].startswith("OK: 2 account(s)")
