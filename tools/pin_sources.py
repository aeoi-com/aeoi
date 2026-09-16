"""Pinned source documents: manifest, download and hash check, SOURCES.md generation.

    python tools/pin_sources.py            # verify hashes of present files, rewrite docs/SOURCES.md
    python tools/pin_sources.py --fetch    # also download files that are missing
    python tools/pin_sources.py --add PATH URL   # add a local file to the manifest (hash computed)

The manifest is ``docs/sources/manifest.json``. OECD files are committed (CC BY 4.0). The ESTV
PDFs are not committed: Swiss federal official documents are likely free of copyright (URG Art. 5),
but "likely" is not enough for a public repository, and the manifest makes them reproducible.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "sources" / "manifest.json"
USER_AGENT = "Mozilla/5.0 (aeoi pin_sources)"

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
  Not committed; `python tools/pin_sources.py --fetch` downloads them and checks the hash.

## Licences and citations

OECD material is published under CC BY 4.0 (OECD open access policy; pre-July-2024 items may be
copied and distributed for commercial and non-commercial purposes with attribution). Citations in the
form the OECD requests:

{citations}

Swiss federal documents: official acts, decisions and reports of authorities are not protected by
copyright (URG Art. 5); a Wegleitung is probably covered but not certainly, hence not redistributed.
"""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> list[dict]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_manifest(entries: list[dict]) -> None:
    MANIFEST.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def verify(entries: list[dict], do_fetch: bool) -> bool:
    ok = True
    for e in entries:
        path = ROOT / e["path"]
        if not path.exists():
            if do_fetch:
                print(f"downloading {e['path']}")
                path.parent.mkdir(parents=True, exist_ok=True)
                fetch(e["url"], path)
            else:
                print(f"MISSING  {e['path']} (run with --fetch)")
                ok = False
                continue
        digest = sha256_of(path)
        if digest != e["sha256"]:
            print(f"HASH MISMATCH {e['path']}: {digest} != {e['sha256']}")
            ok = False
        else:
            print(f"ok       {e['path']}")
    return ok


def write_sources_md(entries: list[dict]) -> None:
    today = datetime.datetime.now(tz=datetime.UTC).date().isoformat()
    lines = [
        "# Pinned sources",
        "",
        (
            f"Manifest: `docs/sources/manifest.json` (regenerated {today}). File names encode the "
            "version the document declares; the hash pins the exact bytes. "
            "`python tools/pin_sources.py --fetch` downloads what is missing and checks every hash."
        ),
        "",
        "| File | Bytes | SHA-256 | Committed | URL |",
        "|---|---|---|---|---|",
    ]
    for e in entries:
        committed = "yes" if e.get("committed", True) else "no"
        lines.append(
            f"| `{e['path']}` | {e['bytes']} | `{e['sha256']}` | {committed} | {e['url']} |"
        )
    citations = "\n".join(f"- {e['citation']}" for e in entries if e.get("citation"))
    (ROOT / "docs" / "SOURCES.md").write_text(
        "\n".join(lines) + "\n" + NOTES.format(citations=citations), encoding="utf-8"
    )


def add_entry(entries: list[dict], path: str, url: str) -> None:
    p = ROOT / path
    entries.append(
        {"path": path, "url": url, "bytes": p.stat().st_size, "sha256": sha256_of(p),
         "committed": True, "citation": ""}
    )  # fmt: skip


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download missing files")
    ap.add_argument(
        "--add", nargs=2, metavar=("PATH", "URL"), help="add a local file to the manifest"
    )
    args = ap.parse_args(argv)
    entries = load_manifest()
    if args.add:
        add_entry(entries, *args.add)
        save_manifest(entries)
    ok = verify(entries, args.fetch)
    write_sources_md(entries)
    print("wrote docs/SOURCES.md")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
