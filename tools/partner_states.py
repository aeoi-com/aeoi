"""Refresh src/aeoi/estv/partner_states.json from the SIF list of Swiss AEOI partner states.

    python tools/partner_states.py                 # download the SIF page, parse, write the JSON
    python tools/partner_states.py --from FILE     # parse a saved copy of the page instead

Source: https://www.sif.admin.ch/de/automatischer-informationsaustausch-aia — "Die nachstehende
Liste enthält die AIA-Partnerstaaten der Schweiz. Sie wird regelmässig aktualisiert und ist
massgebend gegenüber den Listen der OECD." The table (state, parliamentary business number,
Inkrafttreten) is embedded in the page's Nuxt payload; the footnote markers are kept as notes.
Footnote 2 of the page: from the entry into force on 1 January of a year the state counts as a
participating state and reporting FIs collect data from that year on.

The JSON records the "Stand per" date printed on the page, the retrieval date and the SHA-256 of
the downloaded page, so the list is pinned like every other source.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gettext
import hashlib
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

import pycountry

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "aeoi" / "estv" / "partner_states.json"
URL = "https://www.sif.admin.ch/de/automatischer-informationsaustausch-aia"

MANUAL = {  # German names on the SIF page that the ISO 3166 German translation does not cover
    "cayman inseln": "KY",
    "china (volksrepublik)": "CN",
    "färöer inseln": "FO",
    "niederlande, überseegemeinden (bonaire, saint eustatius, saba)": "BQ",
    "russland": "RU",
    "saint kitts und nevis": "KN",
    "saint-lucia": "LC",
    "saint vincent und die grenadinen": "VC",
    "sint maarten": "SX",
    "turks und caicos inseln": "TC",
}
FOOTNOTES = {
    "3": "permanently non-reciprocal",
    "4": "UK: multilateral basis since 01.01.2021",
    "5": "temporarily non-reciprocal",
    "7": "exchange blocked by the Global Forum (security incident); data still collected",
    "8": "multilateral basis since 01.01.2024",
    "9": "transmission to Russia suspended; data still collected and delivered to the ESTV",
}


def german_names() -> dict[str, str]:
    de = gettext.translation("iso3166-1", pycountry.LOCALES_DIR, languages=["de"])
    names: dict[str, str] = {}
    for c in pycountry.countries:
        for attr in ("name", "official_name", "common_name"):
            n = getattr(c, attr, None)
            if n:
                names[de.gettext(n).lower()] = c.alpha_2
                names[n.lower()] = c.alpha_2
    names.update(MANUAL)
    return names


def parse(page: str) -> tuple[list[dict], str]:
    m = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', page, re.DOTALL)
    if not m:
        raise SystemExit("Nuxt payload not found - the SIF page changed; adapt the parser")
    data = json.loads(html.unescape(m.group(1)))

    def resolve(i: int, depth: int = 0):
        if depth > 12:
            return None
        v = data[i]
        if isinstance(v, dict):
            return {k: resolve(x, depth + 1) if isinstance(x, int) else x for k, x in v.items()}
        if isinstance(v, list):
            return [resolve(x, depth + 1) if isinstance(x, int) else x for x in v]
        return v

    names = german_names()
    rows = []
    for v in data:
        if not (isinstance(v, list) and len(v) == 3 and all(isinstance(x, int) for x in v)):
            continue
        cells = [data[x] for x in v]
        if not all(isinstance(c, dict) and "cellContent" in c for c in cells):
            continue
        texts, notes = [], []
        for c in cells:
            cc = resolve(c["cellContent"])
            txt = (
                " ".join(x.get("text", "") for x in cc if isinstance(x, dict))
                if isinstance(cc, list)
                else str(cc)
            )
            notes += re.findall(r"<sup>(.*?)</sup>", txt)
            txt = re.sub(r"<sup>.*?</sup>", "", txt)
            texts.append(html.unescape(re.sub(r"<[^>]+>", "", txt)).strip())
        name, business, in_force = texts
        code = names.get(name.lower())
        if not code:
            raise SystemExit(f"no ISO code for {name!r}; add it to MANUAL")
        day, month, year = in_force.split(".")
        rows.append(
            {
                "code": code,
                "name_de": name,
                "in_force": f"{year}-{month}-{day}",
                "in_force_year": int(year),
                "business_number": business,
                "notes": [FOOTNOTES.get(n, f"footnote {n}") for n in notes],
            }
        )
    rows.sort(key=lambda r: r["code"])
    stand = re.search(
        r"Stand per (\d{2}\.\d{2}\.\d{4})", html.unescape(re.sub(r"<[^>]+>", " ", page))
    )
    return rows, stand.group(1) if stand else ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", help="parse this saved HTML instead of downloading")
    args = ap.parse_args(argv)
    if args.src:
        raw = Path(args.src).read_bytes()
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (aeoi)"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
    rows, stand = parse(raw.decode("utf-8", "ignore"))
    codes = [r["code"] for r in rows]
    assert len(codes) == len(set(codes)), "duplicate country code in the list"
    doc = {
        "source_url": URL,
        "source_stand": stand,
        "retrieved": dt.datetime.now(tz=dt.UTC).date().isoformat(),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "count": len(rows),
        "states": rows,
    }
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} partner states, Stand per {stand}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
