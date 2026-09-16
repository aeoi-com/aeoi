"""Regenerate docs/SOURCES.md with SHA-256 hashes of the pinned source documents."""

from __future__ import annotations

import datetime
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OECD = "https://www.oecd.org/content/dam/oecd/en/"
TOPIC = OECD + "topics/policy-issues/tax-transparency-and-international-co-operation/"
PUB = OECD + "publications/reports/"

URLS = {
    "crs-xml-schema-v3.0.zip": TOPIC + "xml-schema-crs.zip",
    "crs-xml-schema-v2.0.zip": TOPIC + "crs-schema-v2.0.zip",
    "crs-status-message-xml-schema-v2.0.zip": TOPIC + "crs-status-message-v2.0.zip",
    "carf-xml-schema-v1.5.zip": TOPIC + "xml-schema-carf-v1.5.zip",
    "carf-status-message-xml-schema-v1.1.zip": TOPIC + "carf-status-message-xml-schema-v1.1.zip",
    "generic-status-message-xml-schema-v2.0.zip": TOPIC
    + "generic-status-message-xml-schema-v2.0.zip",
    "crs-xml-schema-user-guide-v4.0-2024-10.pdf": PUB
    + "2024/10/amended-common-reporting-standard-xml-schema_27960161/dd7ee57a-en.pdf",
    "crs-status-message-user-guide-v3.0-2025-06.pdf": PUB
    + "2025/06/common-reporting-standard-status-message-xml-schema_6b5a1079/6c08db84-en.pdf",
    "crs-xml-schema-user-guide-v3.0-2019-06.pdf": PUB
    + "2019/06/common-reporting-standard-xml-schema-user-guide-for-tax-administrations-version-3-0-june-2019_32dc1e5a/93b6aa4a-en.pdf",
    "crs-status-message-user-guide-v2.0-2019-06.pdf": PUB
    + "2019/06/common-reporting-standard-status-message-xml-schema-user-guide-for-tax-administrations-version-2-0-june-2019_934c12ea/4aaa6516-en.pdf",
    "carf-xml-schema-user-guide-v2.0-2025-07.pdf": PUB
    + "2024/10/crypto-asset-reporting-framework-xml-schema_d15d81d3/578052ec-en.pdf",
    "estv-technische-wegleitung-aia-2026-09.pdf": "https://www.estv.admin.ch/dam/de/sd-web/nawtcd6uyf89/int-aia-technische-wegleitung-de.pdf",
    "estv-wegleitung-aia-2026-01-15.pdf": "https://www.estv.admin.ch/dam/de/sd-web/hEtJr9vx6Ej-/20260115_Wegleitung_D_Publikation_Clean.pdf",
}

NOTES = """
## What is what

- **CRS XML Schema v3.0** (`CrsXML_v3.0.xsd`, namespace `urn:oecd:ties:crs:v3`) with **User Guide v4.0**
  (October 2024): the business rules for the amended CRS. Only version accepted by the ESTV from
  16.01.2027 (Wegleitung 5.3.1).
- **CRS XML Schema v2.0** (`CrsXML_v2.0.xsd`, namespace `urn:oecd:ties:crs:v2`) with **User Guide v3.0**
  (June 2019): the only version the ESTV accepts until 14.12.2026; used to test the transport pipeline
  before the switch.
- **CRS Status Message XML Schema v2.0** with **User Guide v3.0** (June 2025): the error codes the
  portals return; the ESTV rules refer to it (Wegleitung reference [6]).
- **CARF XML Schema v1.5** with **User Guide v2.0** (July 2025) and **CARF Status Message v1.1**:
  second module.
- **ESTV Technische Wegleitung AIA** (September 2026): Swiss portal rules, 67 error codes,
  packaging/encryption, test messages. **ESTV Wegleitung AIA** (15.01.2026): substantive guidance.

Licensing: OECD content published from 1 July 2024 is CC BY 4.0 by default (OECD open access
policy); Swiss federal official documents are not protected by copyright (URG Art. 5).
"""


def main() -> None:
    rows = []
    for sub in ("oecd", "estv"):
        folder = ROOT / "docs" / "sources" / sub
        for path in sorted(folder.iterdir()):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            rel = path.relative_to(ROOT).as_posix()
            rows.append((rel, path.stat().st_size, digest, URLS.get(path.name, "")))
    today = datetime.datetime.now(tz=datetime.UTC).date().isoformat()
    lines = [
        "# Pinned sources",
        "",
        (
            f"Downloaded on {today}. File names encode the version the document declares; "
            "the hash pins the exact bytes. Regenerate with `python tools/pin_sources.py`."
        ),
        "",
        "| File | Bytes | SHA-256 | URL |",
        "|---|---|---|---|",
    ]
    for rel, size, digest, url in rows:
        lines.append(f"| `{rel}` | {size} | `{digest}` | {url} |")
    (ROOT / "docs" / "SOURCES.md").write_text("\n".join(lines) + "\n" + NOTES, encoding="utf-8")
    print(f"wrote docs/SOURCES.md with {len(rows)} rows")


if __name__ == "__main__":
    main()
