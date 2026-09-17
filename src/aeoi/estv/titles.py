"""Human titles and one-line remedies per rule code in de/fr/it/en (``rule_titles.json``).

The official wording stays in the catalogue (``rules_catalogue.json``, German). These titles are
what a user sees first on the browser page and, later, in the CLI.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

TITLES = Path(__file__).with_name("rule_titles.json")
LANGUAGES = ("de", "fr", "it", "en")


@lru_cache(maxsize=1)
def titles() -> dict[str, dict]:
    data = json.loads(TITLES.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def _key(rule: str) -> str:
    if rule in titles():
        return rule
    if rule.startswith("aeoi"):
        return "aeoi"
    return ""


def rule_title(rule: str, lang: str = "de") -> str:
    """Short title for a rule code; the code itself when unknown."""
    entry = titles().get(_key(rule))
    if not entry:
        return rule
    return entry["title"].get(lang) or entry["title"]["de"]


def rule_fix(rule: str, lang: str = "de") -> str:
    entry = titles().get(_key(rule))
    if not entry:
        return ""
    return entry["fix"].get(lang) or entry["fix"]["de"]
