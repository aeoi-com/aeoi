"""XSD validation of CRS documents against the pinned OECD schemas (schema validation = ESTV 50007)."""

from __future__ import annotations

from functools import cache
from pathlib import Path

import xmlschema

from aeoi.crs.model import Version

XSD_DIR = (
    Path(__file__).resolve().parents[1] / "xsd"
)  # copied from /schemas by tools/generate_models.py
SCHEMAS = {
    "2.0": XSD_DIR / "crs_v2.0" / "CrsXML_v2.0.xsd",
    "3.0": XSD_DIR / "crs_v3.0" / "CrsXML_v3.0.xsd",
}


@cache
def schema(version: Version) -> xmlschema.XMLSchema:
    return xmlschema.XMLSchema(SCHEMAS[version])


def validate(xml: str | bytes, version: Version) -> list[str]:
    """Human-readable XSD errors (empty list = valid). Mirrors the portal's schema step (50007)."""
    out = []
    for err in schema(version).iter_errors(xml):
        where = err.path or ""
        out.append(f"{where}: {err.reason}" if err.reason else str(err).splitlines()[0])
    return out
