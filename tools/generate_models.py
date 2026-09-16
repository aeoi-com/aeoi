"""Regenerate src/aeoi/schemas/* from the pinned OECD XSDs with xsdata, then apply known patches.

Run from the repository root with the project virtualenv (ruff must be on PATH for xsdata):

    python tools/generate_models.py

Patch 1 - Address_Type field order. The XSD says ``CountryCode, (AddressFree | (AddressFix,
AddressFree?))``; xsdata flattens the choice into ``address_free`` then ``address_fix``, so a
document with both parts would serialise AddressFree first and fail validation ("AddressFix has
to precede AddressFree"). We move ``address_fix`` before ``address_free``.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCHEMAS = {
    "crs_v3": "crs_v3.0/CrsXML_v3.0.xsd",
    "crs_v2": "crs_v2.0/CrsXML_v2.0.xsd",
    "crs_status_message_v2": "crs_status_message_v2.0/CrsStatusMessageXML_v2.0.xsd",
    "carf_v1_5": "carf_v1.5/CARFXML_v1.5.xsd",
    "carf_status_message_v1_1": "carf_status_message_v1.1/CARFStatusMessageXML_v1.1.xsd",
}

FIELD_RE = r"    {name}: [^\n]*= field\(\n(?:        [^\n]*\n)*?    \)\n"


def generate() -> None:
    for package, xsd in SCHEMAS.items():
        target = SRC / "aeoi" / "schemas" / package
        shutil.rmtree(target, ignore_errors=True)
        cmd = [
            sys.executable,
            "-m",
            "xsdata",
            "generate",
            str(ROOT / "schemas" / xsd),
            "--package",
            f"aeoi.schemas.{package}",
            "--structure-style",
            "filenames",
            "--docstring-style",
            "Google",
        ]
        print(" ".join(cmd[3:]))
        subprocess.run(cmd, cwd=SRC, check=True)


def patch_address_order() -> int:
    patched = 0
    for path in (SRC / "aeoi" / "schemas").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "class AddressType" not in text:
            continue
        free = re.search(FIELD_RE.format(name="address_free"), text)
        fix = re.search(FIELD_RE.format(name="address_fix"), text)
        if not free or not fix or fix.start() < free.start():
            continue
        new = (
            text[: free.start()]
            + fix.group(0)
            + free.group(0)
            + text[free.end() : fix.start()]
            + text[fix.end() :]
        )
        path.write_text(new, encoding="utf-8")
        patched += 1
        print(f"patched Address_Type order in {path.relative_to(ROOT)}")
    return patched


def main() -> None:
    generate()
    n = patch_address_order()
    (SRC / "aeoi" / "schemas" / "__init__.py").write_text(
        '"""Generated from the pinned OECD XSDs by tools/generate_models.py - do not edit."""\n',
        encoding="utf-8",
    )
    print(f"done; {n} file(s) patched")


if __name__ == "__main__":
    main()
