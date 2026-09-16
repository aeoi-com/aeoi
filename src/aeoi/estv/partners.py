"""Swiss AEOI partner states by reporting year (SIF list, pinned in ``partner_states.json``).

Wegleitung 5.3.8-5.3.10 (rules 98200, 98201, 98202): at least one ResCountryCode must be a
partner state "die im Berichtsjahr aktiv waren". SIF footnote 2: a state counts as participating
from the entry into force on 1 January of a year, so ``in_force_year <= reporting_year``.
Non-reciprocal and suspended states (e.g. Russia) stay in the list: FIs must still collect and
deliver the data. Refresh with ``python tools/partner_states.py``.

The SIF page shows only the current state of the list; "active in the reporting year" for past
years is reconstructed from the entry-into-force dates. No state has ever left the list, so the
reconstruction coincides with history today; if a state is removed one day, the JSON needs an
``until`` field and this module a second condition. The pin is ``table_sha256`` (canonical
table) plus ``source_stand``; the page hash is informational because the page is dynamic.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).with_name("partner_states.json")


@lru_cache(maxsize=1)
def _load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def source() -> dict:
    """Provenance: URL, 'Stand per' date, retrieval date, table hash (pin), page hash (info)."""
    d = _load()
    keys = ("source_url", "source_stand", "retrieved", "table_sha256", "page_sha256", "count")
    return {k: d[k] for k in keys}


def table_sha256() -> str:
    """Recompute the canonical hash from the states (must equal the stored pin)."""
    import hashlib
    import json as _json

    canonical = _json.dumps(
        _load()["states"], sort_keys=True, ensure_ascii=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@lru_cache(maxsize=32)
def partner_codes(reporting_year: int) -> frozenset[str]:
    """ISO alpha-2 codes of the states that were partner states in the reporting year."""
    return frozenset(s["code"] for s in _load()["states"] if s["in_force_year"] <= reporting_year)


def is_partner(code: str, reporting_year: int) -> bool:
    return code in partner_codes(reporting_year)


def notes(code: str) -> list[str]:
    for s in _load()["states"]:
        if s["code"] == code:
            return list(s["notes"])
    return []
