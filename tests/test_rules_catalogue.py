"""The ESTV rules catalogue is complete and every 'implemented' code is referenced in the code base."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "src" / "aeoi" / "estv" / "rules_catalogue.json"


def _entries():
    return json.loads(CATALOGUE.read_text(encoding="utf-8"))


def test_catalogue_has_the_65_rule_codes():
    entries = _entries()
    codes = [e["code"] for e in entries]
    assert len(codes) == 65 and len(set(codes)) == 65
    assert "98999" not in codes and "70012" not in codes
    for e in entries:
        assert e["status"] in {"implemented", "registry", "portal"}, e
        assert 17 <= e["page"] <= 35, e


def test_implemented_codes_are_referenced_in_sources_or_tests():
    text = ""
    for folder in (ROOT / "src" / "aeoi", ROOT / "tests"):
        for path in folder.rglob("*.py"):
            if "schemas" in path.parts or path.name == "test_rules_catalogue.py":
                continue
            text += path.read_text(encoding="utf-8")
    missing = [
        e["code"]
        for e in _entries()
        if e["status"] == "implemented" and not re.search(rf"\b{e['code']}\b", text)
    ]
    assert not missing, f"implemented in the catalogue but never mentioned in code/tests: {missing}"


def test_registry_codes_are_the_correction_family():
    registry = {e["code"] for e in _entries() if e["status"] == "registry"}
    assert registry == {
        "50009", "80000", "80002", "80003", "80005", "80008", "80010", "80011",
        "98009", "98102", "98103", "98204",
    }  # fmt: skip
