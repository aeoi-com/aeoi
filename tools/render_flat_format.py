"""Render docs/FLAT-FORMAT.md from the column definitions in aeoi.crs.flat (single source of truth)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aeoi.crs import flat

INTRO = """# Flat input format (contract)

Generated from `src/aeoi/crs/flat.py` by `python tools/render_flat_format.py` — edit the code, not
this file. The Excel template (`aeoi crs template --out template.xlsx`) is generated from the same
definitions; `--example` fills it with invented data.

One workbook (or one folder of `<Sheet>.csv` files, `;`-separated, UTF-8) = one reporting FI = one
CRS message. Sheets: `ReportingFI` (field/value rows), `Accounts` (one row per account, holder
inline), `ControllingPersons` and `Payments` (linked to the account by `key`).

Conventions: several values in one cell are separated by `;`; TINs/INs are `value@CC`
(issuing country optional); booleans accept true/false, 1/0, yes/no, ja/nein, oui/non; dates are
`YYYY-MM-DD`, `DD.MM.YYYY` or Excel dates; amounts are numbers with a dot (or Excel numbers).
Codes are the OECD values (see `src/aeoi/crs/codes.py` and the `Codes` sheet). Columns marked
"3.0" are mandatory for CRS schema 3.0 and ignored for 2.0. Empty `doc_ref_id` cells are filled
with generated `CH<year>CH<uuid>` identifiers at build time.

"""


def table(columns: list[flat.Column]) -> str:
    lines = ["| column | required | kind | description |", "|---|---|---|---|"]
    for c in columns:
        codes = f" Codes: {', '.join(c.codes)}." if c.codes else ""
        lines.append(
            f"| `{c.name}` | {'yes' if c.required else ''} | {c.kind} | {c.description}{codes} |"
        )
    return "\n".join(lines)


def main() -> None:
    parts = [INTRO]
    for name, columns in flat.SHEETS.items():
        parts.append(f"## {name}\n\n{table(columns)}\n")
    (ROOT / "docs" / "FLAT-FORMAT.md").write_text("\n".join(parts), encoding="utf-8")
    print("wrote docs/FLAT-FORMAT.md")


if __name__ == "__main__":
    main()
