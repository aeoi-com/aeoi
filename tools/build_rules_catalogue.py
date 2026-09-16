"""Build src/aeoi/estv/rules_catalogue.json and docs/ESTV-RULES.md.

The rule text and page come from the Technische Wegleitung AIA (ESTV, 09.2026); the status says
where the toolkit enforces the rule:

- implemented: enforced before the file leaves the machine (model checks, builder by
  construction, packaging, XSD validation)
- registry: needs the local submission registry / corrections (none left since week 4)
- portal: can only be checked by the ESTV portal (transport, decryption, virus scan,
  registration of the FI, history the portal alone knows)

Numbers that are not rules: 98999 is the upper bound of the ESTV range "98000-98999", 70012 is
mentioned only in the change log (rule removed in a later edition). 65 rule codes remain.
Three OECD codes the ESTV does not list are added with origin "oecd" (50013, 60011, 60012).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pypdf

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "docs" / "sources" / "estv" / "estv-technische-wegleitung-aia-2026-09.pdf"
OUT = ROOT / "src" / "aeoi" / "estv" / "rules_catalogue.json"
DOC = ROOT / "docs" / "ESTV-RULES.md"
NOT_RULES = {"98999", "70012"}
FILE_TABLE_CODES = {"50001", "50002", "50003", "50004", "50006", "50007"}
HEADING_RE = re.compile(r"(5\.\d(?:\.\d+)?) ([A-Z][A-Za-z_.]+)")
CODE_RE = re.compile(r"\b([5-9]\d{4})\b")
TABLE_HEADER = "Regel Validierung Fehlercode"

STATUS: dict[str, tuple[str, str]] = {  # code -> (status, where / note)
    "50001": ("portal", "transport error"),
    "50002": ("portal", "decryption by the ESTV (aeoi.estv.packaging builds the package)"),
    "50003": ("portal", "decompression by the ESTV"),
    "50004": ("portal", "signature check of the package by the ESTV"),
    "50005": ("implemented", "aeoi.estv.ids.invalid_characters via model._check_text on every text element"),
    "50006": ("portal", "virus scan"),
    "50007": ("implemented", "aeoi.crs.xsd.validate before writing/packaging; XML never signed"),
    "50008": ("implemented", "aeoi.estv.ids.message_ref_id / check_message_ref_id; build"),
    "50009": ("implemented", "aeoi.registry: MessageRefId never reused (assert_message_ref_id_unused)"),
    "50010": ("implemented", "packaging.check_file_name + build(test=False) writes OECD1 only"),
    "50011": ("implemented", "packaging.check_file_name + build(test=True) writes OECD11 only"),
    "50012": ("implemented", "build: ReceivingCountry = CH"),
    "60000": ("implemented", "aeoi.crs.checksums.is_valid_iban; model._check_account_number"),
    "60001": ("implemented", "aeoi.crs.checksums.is_valid_isin; model._check_account_number"),
    "60002": ("implemented", "model.check_account: balance >= 0"),
    "60003": ("implemented", "model.check_account: closed -> balance 0"),
    "60004": ("implemented", "model: nameType OECD201 refused (holder, organisation); build writes OECD207 for the FI"),
    "60005": ("implemented", "model.check_account: no controlling persons for individuals / CRS102 / CRS103"),
    "60006": ("implemented", "model.check_account: CRS101 needs controlling persons"),
    "60007": ("implemented", "build: exactly one ReportingGroup"),
    "60008": ("implemented", "build: Sponsor never written"),
    "60009": ("implemented", "build: Intermediary never written"),
    "60010": ("implemented", "build: PoolReport never written"),
    "60013": ("implemented", "build: ReportingFI.ResCountryCode = CH = TransmittingCountry"),
    "60014": ("implemented", "model._check_person: 1900-01-01 < birth date < today"),
    "60015": ("implemented", "model.check_message: accounts required unless CRS703"),
    "60017": ("implemented", "model.check_account: OECD606 -> CRS1101"),
    "60018": ("implemented", "model.check_account: OECD601 -> CRS1101 (prose; the formula in the Wegleitung says OECD606 by mistake)"),
    "60019": ("implemented", "model.check_account: EquityInterestType -> CRS1104"),
    "60020": ("implemented", "model.check_account: CRS1103 -> OECD605"),
    "60021": ("implemented", "model.check_account: CRS1101 -> payments CRS502 only ('Tyoe' typo in the Wegleitung)"),
    "60022": ("implemented", "model.check_account: CRS1104 -> CRS503/CRS504"),
    "60023": ("implemented", "model.check_account: CRS1103 -> CRS503/CRS504"),
    "70015": ("implemented", "model.check_message: UID format when given; build omits IN otherwise"),
    "80000": ("implemented", "model: unique in the file; aeoi.registry: never reused across messages"),
    "80001": ("implemented", "aeoi.estv.ids.doc_ref_id / check_doc_ref_id; build"),
    "80002": ("implemented", "aeoi.registry.correction_target: CorrDocRefId = last valid DocRefId of this FI"),
    "80003": ("implemented", "aeoi.registry: only the chain head can be corrected (superseded_by)"),
    "80004": ("implemented", "build: ReportingFI DocSpec never carries CorrDocRefId"),
    "80005": ("implemented", "aeoi.crs.build RecordPlan: OECD2/OECD3 always carry CorrDocRefId"),
    "80006": ("implemented", "build: CorrMessageRefId never written in DocSpec"),
    "80007": ("implemented", "build: MessageSpec.CorrMessageRefId never written"),
    "80008": ("implemented", "aeoi.crs.submit: AccountReports never OECD0; only the ReportingFI is resent"),
    "80010": ("implemented", "aeoi.crs.submit: CRS701 -> OECD1 only, CRS702 -> OECD2/OECD3 only; model refuses CRS702 without the registry"),
    "80011": ("implemented", "aeoi.crs.submit.plan_correction: one CorrDocRefId per message"),
    "98000": ("implemented", "build: version attribute 2.0 / 3.0 with the matching namespace"),
    "98001": ("implemented", "model: ESTV-ID present (format only a warning); the portal compares with the registration"),
    "98002": ("implemented", "build: TransmittingCountry = CH"),
    "98003": ("portal", "FI registered for the reporting year"),
    "98004": ("implemented", "model.check_message: MessageTypeIndic present and valid"),
    "98005": ("implemented", "model.check_message: CRS703 without accounts"),
    "98006": ("implemented", "build: ReportingPeriod = 31.12 of the MessageRefId year"),
    "98007": ("implemented", "model.check_message: reporting year <= current year"),
    "98008": ("implemented", "build: Timestamp = now (UTC)"),
    "98009": ("implemented", "aeoi.crs.submit.build_new: nil report refused while valid records exist"),
    "98100": ("implemented", "build: exactly one CrsBody"),
    "98101": ("implemented", "build: ReportingFI DocTypeIndic OECD1 or OECD11 only"),
    "98102": ("implemented", "aeoi.crs.submit: ReportingFI resent as OECD0 with its DocRefId"),
    "98103": ("implemented", "aeoi.registry.correction_target: a deleted record (OECD3) cannot be corrected"),
    "98104": ("implemented", "model._check_address: City mandatory (AddressFix)"),
    "98200": ("implemented", "model._check_partner_states with the SIF list by year; undocumented exception"),
    "98201": ("implemented", "model._check_partner_states; controlling-person fallback"),
    "98202": ("implemented", "model._check_partner_states for controlling persons"),
    "98203": ("implemented", "model.check_account: undocumented -> individual with ResCountryCode CH"),
    "98204": ("implemented", "aeoi.crs.submit: deletions reuse the stored account content (same ResCountryCodes)"),
}  # fmt: skip

OECD_EXTRA: list[dict] = [  # OECD Status Message codes the ESTV does not list for FI -> ESTV
    {
        "code": "50013",
        "section": "OECD CRS Status Message User Guide v3.0, II.13",
        "page": 0,
        "text_de": "AES key size incorrect: cipher mode other than CBC, IV missing in the key file, "
        "key blob not 48 bytes",
        "status": "implemented",
        "where": "aeoi.estv.packaging by construction: AES-256-CBC, fresh 16-byte IV, 48-byte key blob",
    },
    {
        "code": "60011",
        "section": "OECD CRS Status Message User Guide v3.0 (data sorting)",
        "page": 0,
        "text_de": "Person ResCountryCode must match the message ReceivingCountry",
        "status": "portal",
        "where": "CA-to-CA sorting rule; for FI -> ESTV superseded by 98200 / 98202",
    },
    {
        "code": "60012",
        "section": "OECD CRS Status Message User Guide v3.0 (data sorting)",
        "page": 0,
        "text_de": "Organisation or controlling-person ResCountryCode must match the ReceivingCountry",
        "status": "portal",
        "where": "CA-to-CA sorting rule; for FI -> ESTV superseded by 98201",
    },
]  # fmt: skip


def extract() -> dict[str, dict]:
    """Every ESTV code with its section (headings are cumulative across pages) and the rule text
    of the occurrence that sits in a 'Regel | Validierung | Fehlercode' table; a code with several
    table rows (50010, 50011, 98204) keeps every distinct wording."""
    reader = pypdf.PdfReader(PDF)
    flat = ""
    page_at: list[tuple[int, int]] = []  # (offset in flat, page number)
    for pi, page in enumerate(reader.pages):
        if pi < 10:  # cover, change log, table of contents
            continue
        page_at.append((len(flat), pi + 1))
        flat += re.sub(r"\s+", " ", page.extract_text() or "") + " "
    headings = [(m.start(), f"{m.group(1)} {m.group(2)}") for m in HEADING_RE.finditer(flat)]

    def page_of(pos: int) -> int:
        return max(n for off, n in page_at if off <= pos)

    def section_of(pos: int) -> str:
        before = [h for off, h in headings if off < pos]
        return before[-1] if before else ""

    def row_text(m: re.Match) -> str | None:
        """Text of the table row that ends with this code; None when the code is prose."""
        start = max(0, m.start() - 700)
        window = flat[start : m.start()]
        table = window.rfind(TABLE_HEADER)
        prev_codes = list(CODE_RE.finditer(window))
        if table == -1 and not prev_codes:
            return None
        cuts = [c.end() for c in prev_codes]
        if table != -1:
            cuts.append(table + len(TABLE_HEADER))
        row = window[max(cuts) :].strip()
        if HEADING_RE.search(row):  # a section heading inside the "row": prose, not a table
            return None
        return row

    entries: dict[str, dict] = {}
    for m in CODE_RE.finditer(flat):
        code = m.group(1)
        if code in NOT_RULES:
            continue
        if code in FILE_TABLE_CODES:  # file/schema tables read "Failed X <code> <description>"
            after = flat[m.end() : m.end() + 200]
            text = re.split(r" Failed | Hinweis:| 5\.\d", after)[0].strip()
        elif code == "50005":
            text = (
                "Datenelemente duerfen nur Zeichen aus ISO 8859-1 ohne die Ausnahmen des Anhangs "
                "7.2 enthalten; ungueltige Zeichen werden als Fehler 50005 zurueckgemeldet"
            )
        else:
            text = row_text(m)
            if text is None:
                continue  # prose mention (e.g. "Fehlercodes 98000-98999"), not a rule row
        text = text[-300:]
        status, where = STATUS[code]
        entry = entries.get(code)
        if entry is None:
            entries[code] = {
                "code": code,
                "section": section_of(m.start()),
                "page": page_of(m.start()),
                "text_de": text,
                "texts_de": [text],
                "status": status,
                "where": where,
                "origin": "estv",
            }
        else:
            here = f"{section_of(m.start())} (p. {page_of(m.start())})"
            if (
                here.split(" (p.")[0] != entry["section"].split(";")[0]
                and here not in entry["section"]
            ):
                entry["section"] += f"; {here}"
            if text not in entry["texts_de"]:
                entry["texts_de"].append(text)
    for extra in OECD_EXTRA:
        entries[extra["code"]] = {**extra, "texts_de": [extra["text_de"]], "origin": "oecd"}
    return dict(sorted(entries.items()))


def render(entries: dict[str, dict]) -> str:
    estv = [e for e in entries.values() if e["origin"] == "estv"]
    counts = {
        s: sum(1 for e in estv if e["status"] == s) for s in ("implemented", "registry", "portal")
    }
    lines = [
        "# ESTV validation rules — coverage",
        "",
        "Source: Technische Wegleitung AIA (ESTV, September 2026), sections 5.1-5.3.11. Generated by",
        "`python tools/build_rules_catalogue.py` from `src/aeoi/estv/rules_catalogue.json`.",
        "",
        (
            f"{len(estv)} ESTV rule codes: **{counts['implemented']} implemented** in the toolkit, "
            f"**{counts['registry']}** waiting for the submission registry / corrections, "
            f"**{counts['portal']}** checkable only by the portal. (98999 is a range bound and "
            "70012 a change-log reference, not rules.)"
        ),
        "",
        "OECD CRS Status Message User Guide v3.0 (schema 2.0) codes absent from the ESTV list:",
        "50013, 60011 and 60012 are in the table with origin `oecd`; 60016 equals ESTV 60005;",
        "70000/70002/70003/70012 were deleted by User Guide v3.0, so the ESTV cannot return them;",
        "80009 and 80012-80015 concern resend and CA-to-CA cases the builder never produces (one",
        "reporting period per message by construction); 90000-90002 (TIN structure/algorithm) are",
        "not applied by the ESTV, which states TINs cannot be validated technically - a",
        "per-jurisdiction TIN warning may come later; 99999 is the custom error.",
        "",
        "| code | origin | section | page | status | where | rule (excerpt) |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in entries.values():
        text = " ‖ ".join(t.replace("|", "/") for t in e["texts_de"])
        page = e["page"] or "-"
        lines.append(
            f"| {e['code']} | {e['origin']} | {e['section']} | {page} | {e['status']} | "
            f"{e['where']} | {text} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    entries = extract()
    estv_codes = {c for c, e in entries.items() if e["origin"] == "estv"}
    missing = set(STATUS) - estv_codes
    extra = estv_codes - set(STATUS)
    if missing or extra:
        print(f"catalogue mismatch: missing {sorted(missing)}, extra {sorted(extra)}")
        return 1
    OUT.write_text(
        json.dumps(list(entries.values()), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    DOC.write_text(render(entries), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}: {len(entries)} codes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
