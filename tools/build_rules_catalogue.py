"""Build src/aeoi/estv/rules_catalogue.json and docs/ESTV-RULES.md.

The rule text and page come from the Technische Wegleitung AIA (ESTV, 09.2026); the status says
where the toolkit enforces the rule:

- implemented: enforced before the file leaves the machine (model checks, builder by
  construction, packaging, XSD validation)
- registry: needs the local submission registry / corrections (week 4)
- portal: can only be checked by the ESTV portal (transport, decryption, virus scan,
  registration of the FI, history the portal alone knows)

Numbers that are not rules: 98999 is the upper bound of the ESTV range "98000-98999", 70012 is
mentioned only in the change log (rule removed in a later edition). 65 rule codes remain.
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

STATUS: dict[str, tuple[str, str]] = {  # code -> (status, where / note)
    "50001": ("portal", "transport error"),
    "50002": ("portal", "decryption by the ESTV (aeoi.estv.packaging builds the package)"),
    "50003": ("portal", "decompression by the ESTV"),
    "50004": ("portal", "signature check of the package by the ESTV"),
    "50005": (
        "implemented",
        "aeoi.estv.ids.invalid_characters via model._check_text on every text element",
    ),
    "50006": ("portal", "virus scan"),
    "50007": ("implemented", "aeoi.crs.xsd.validate before writing/packaging; XML never signed"),
    "50008": ("implemented", "aeoi.estv.ids.message_ref_id / check_message_ref_id; build"),
    "50009": ("registry", "MessageRefId never reused: UUID today, registry check later"),
    "50010": ("implemented", "packaging.check_file_name + build(test=False) writes OECD1 only"),
    "50011": ("implemented", "packaging.check_file_name + build(test=True) writes OECD11 only"),
    "50012": ("implemented", "build: ReceivingCountry = CH"),
    "60000": ("implemented", "aeoi.crs.checksums.is_valid_iban; model._check_account_number"),
    "60001": ("implemented", "aeoi.crs.checksums.is_valid_isin; model._check_account_number"),
    "60002": ("implemented", "model.check_account: balance >= 0"),
    "60003": ("implemented", "model.check_account: closed -> balance 0"),
    "60004": (
        "implemented",
        "model: nameType OECD201 refused (holder, organisation); build writes OECD207 for the FI",
    ),
    "60005": (
        "implemented",
        "model.check_account: no controlling persons for individuals / CRS102 / CRS103",
    ),
    "60006": ("implemented", "model.check_account: CRS101 needs controlling persons"),
    "60007": ("implemented", "build: exactly one ReportingGroup"),
    "60008": ("implemented", "build: Sponsor never written"),
    "60009": ("implemented", "build: Intermediary never written"),
    "60010": ("implemented", "build: PoolReport never written"),
    "60013": ("implemented", "build: ReportingFI.ResCountryCode = CH = TransmittingCountry"),
    "60014": ("implemented", "model._check_person: 1900-01-01 < birth date < today"),
    "60015": ("implemented", "model.check_message: accounts required unless CRS703"),
    "60017": ("implemented", "model.check_account: OECD606 -> CRS1101"),
    "60018": (
        "implemented",
        "model.check_account: OECD601 -> CRS1101 (prose; the formula in the Wegleitung says OECD606 by mistake)",
    ),
    "60019": ("implemented", "model.check_account: EquityInterestType -> CRS1104"),
    "60020": ("implemented", "model.check_account: CRS1103 -> OECD605"),
    "60021": (
        "implemented",
        "model.check_account: CRS1101 -> payments CRS502 only ('Tyoe' typo in the Wegleitung)",
    ),
    "60022": ("implemented", "model.check_account: CRS1104 -> CRS503/CRS504"),
    "60023": ("implemented", "model.check_account: CRS1103 -> CRS503/CRS504"),
    "70015": (
        "implemented",
        "model.check_message: UID format when given; build omits IN otherwise",
    ),
    "80000": (
        "registry",
        "unique within the file today (model); against all earlier messages with the registry",
    ),
    "80001": ("implemented", "aeoi.estv.ids.doc_ref_id / check_doc_ref_id; build"),
    "80002": ("registry", "CorrDocRefId must be an earlier DocRefId of the same FI"),
    "80003": ("registry", "a record may be corrected once per chain"),
    "80004": ("implemented", "build: ReportingFI DocSpec never carries CorrDocRefId"),
    "80005": ("registry", "corrections/deletions need CorrDocRefId"),
    "80006": ("implemented", "build: CorrMessageRefId never written in DocSpec"),
    "80007": ("implemented", "build: MessageSpec.CorrMessageRefId never written"),
    "80008": (
        "registry",
        "Resend Data (OECD0/OECD10) not used by the builder; rule complete with corrections",
    ),
    "80010": (
        "registry",
        "CRS702 refused today (model); DocTypeIndic/MessageTypeIndic consistency with corrections",
    ),
    "80011": ("registry", "CorrDocRefId unique within a correction message"),
    "98000": ("implemented", "build: version attribute 2.0 / 3.0 with the matching namespace"),
    "98001": (
        "implemented",
        "model: ESTV-ID present (format only a warning); the portal compares with the registration",
    ),
    "98002": ("implemented", "build: TransmittingCountry = CH"),
    "98003": ("portal", "FI registered for the reporting year"),
    "98004": ("implemented", "model.check_message: MessageTypeIndic present and valid"),
    "98005": ("implemented", "model.check_message: CRS703 without accounts"),
    "98006": ("implemented", "build: ReportingPeriod = 31.12 of the MessageRefId year"),
    "98007": ("implemented", "model.check_message: reporting year <= current year"),
    "98008": ("implemented", "build: Timestamp = now (UTC)"),
    "98009": ("registry", "no nil report after data for the same year"),
    "98100": ("implemented", "build: exactly one CrsBody"),
    "98101": ("implemented", "build: ReportingFI DocTypeIndic OECD1 or OECD11 only"),
    "98102": ("registry", "resend keeps the DocRefId"),
    "98103": ("registry", "a deleted record cannot be corrected again"),
    "98104": ("implemented", "model._check_address: City mandatory (AddressFix)"),
    "98200": (
        "implemented",
        "model._check_partner_states with the SIF list by year; undocumented exception",
    ),
    "98201": ("implemented", "model._check_partner_states; controlling-person fallback"),
    "98202": ("implemented", "model._check_partner_states for controlling persons"),
    "98203": (
        "implemented",
        "model.check_account: undocumented -> individual with ResCountryCode CH",
    ),
    "98204": ("registry", "deletion carries the ResCountryCodes of the deleted record"),
}


def extract() -> dict[str, dict]:
    reader = pypdf.PdfReader(PDF)
    entries: dict[str, dict] = {}
    section = ""
    for pi, page in enumerate(reader.pages):
        if pi < 10:  # skip cover, history and table of contents
            continue
        flat = re.sub(r"\s+", " ", page.extract_text() or "")
        for m in re.finditer(r"\b([5-9]\d{4})\b", flat):
            code = m.group(1)
            if code in NOT_RULES or code in entries:
                continue
            start = max(0, m.start() - 420)
            prev = flat[start : m.start()]
            prev_codes = list(re.finditer(r"\b[5-9]\d{4}\b", prev))
            if prev_codes:
                prev = prev[prev_codes[-1].end() :]
            prev = re.sub(r"Regel Validierung Fehlercode", "", prev).strip()
            if code in {"50001", "50002", "50003", "50004", "50006", "50007"}:
                # file/schema tables read "Failed X <code> <description>"
                after = flat[m.end() : m.end() + 200]
                after = re.split(r" Failed | Hinweis:| 5\.\d", after)[0]
                prev = after.strip()
            secs = re.findall(r"(5\.\d(?:\.\d+)?) ([A-Z][A-Za-z.]+)", flat[: m.start()])
            if secs:
                section = " ".join(secs[-1])
            status, where = STATUS[code]
            entries[code] = {
                "code": code,
                "section": section,
                "page": pi + 1,
                "text_de": prev[-300:],
                "status": status,
                "where": where,
            }
    return dict(sorted(entries.items()))


def render(entries: dict[str, dict]) -> str:
    counts = {
        s: sum(1 for e in entries.values() if e["status"] == s)
        for s in ("implemented", "registry", "portal")
    }
    lines = [
        "# ESTV validation rules — coverage",
        "",
        "Source: Technische Wegleitung AIA (ESTV, September 2026), sections 5.1-5.3.11. Generated by",
        "`python tools/build_rules_catalogue.py` from `src/aeoi/estv/rules_catalogue.json`.",
        "",
        (
            f"{len(entries)} rule codes: **{counts['implemented']} implemented** in the toolkit, "
            f"**{counts['registry']}** waiting for the submission registry / corrections, "
            f"**{counts['portal']}** checkable only by the portal. (98999 is a range bound and "
            "70012 a change-log reference, not rules.)"
        ),
        "",
        "| code | section | page | status | where | rule (German, excerpt) |",
        "|---|---|---|---|---|---|",
    ]
    for e in entries.values():
        text = e["text_de"].replace("|", "/")
        lines.append(
            f"| {e['code']} | {e['section']} | {e['page']} | {e['status']} | {e['where']} | {text} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    entries = extract()
    missing = set(STATUS) - set(entries)
    extra = set(entries) - set(STATUS)
    if missing or extra:
        print(f"catalogue mismatch: missing {sorted(missing)}, extra {sorted(extra)}")
        return 1
    OUT.write_text(
        json.dumps(list(entries.values()), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    DOC.write_text(render(entries), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}: {len(entries)} rules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
