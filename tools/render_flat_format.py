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
with generated `CH<year>CH<uuid>` identifiers at build time; a DocRefId can never be reused
(ESTV 80000), so fill the column only with identifiers that have never been sent.

Joint accounts: one row per reportable holder, same `account_number`, the full balance on each
row, and for 3.0 `joint_account_number` = number of joint holders on every row. Trustee-documented
trusts: the trust's name in `ReportingFI.name` plus `trustee_documented_trust = true`; the builder
writes `TDT=` before the name (ESTV 5.3.4). `uid` may be empty when the FI has no UID (70015).
Corrections (`CRS702`) are built only through `aeoi crs correct` with the submission registry: changed rows become OECD2, `--cancel KEY` rows OECD3, unchanged rows are left out, new rows must go into a new `aeoi crs build` message.

"""


def table(columns: list[flat.Column]) -> str:
    lines = ["| column | required | kind | description |", "|---|---|---|---|"]
    for c in columns:
        codes = f" Codes: {', '.join(c.codes)}." if c.codes else ""
        required = "yes" if c.required is True else (f"if {c.required}" if c.required else "")
        lines.append(f"| `{c.name}` | {required} | {c.kind} | {c.description}{codes} |")
    return "\n".join(lines)


def main() -> None:
    parts = [INTRO]
    for name, columns in flat.SHEETS.items():
        parts.append(f"## {name}\n\n{table(columns)}\n")
    (ROOT / "docs" / "FLAT-FORMAT.md").write_text("\n".join(parts), encoding="utf-8")
    print("wrote docs/FLAT-FORMAT.md")


if __name__ == "__main__":
    main()
