"""Reading the validation outcome of a submission.

Two inputs are supported, because the exact format the ESTV portal returns is still an open
question (docs/OPEN-QUESTIONS.md, item 4):

1. An OECD **CRS Status Message XML** (schema 2.0, ``urn:oecd:ties:csm:v2``). The Wegleitung says
   the ESTV rules and codes follow the CRS Status Message User Guide v3.0 and that the result can
   be fetched via the M2M interface, so this is the expected machine format.
2. **Plain text** copied from the portal's message overview by the pilot: any line containing a
   five-digit code, optionally a DocRefId (``CH<year>CH...``); everything else is kept as detail.

Both become the same :class:`Outcome`; codes are looked up in the ESTV rules catalogue so the
report shows the rule text, the section and whether the toolkit should have caught it.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from xsdata.formats.dataclass.parsers import XmlParser

from aeoi.schemas.crs_status_message_v2.crs_status_message_xml_v2_0 import CrsstatusMessageOecd

CATALOGUE = Path(__file__).with_name("rules_catalogue.json")
CODE_RE = re.compile(r"\b([5-9]\d{4})\b")
DOC_REF_RE = re.compile(r"\bCH\d{4}CH[0-9A-Za-z._-]{1,42}\b")
MSG_REF_RE = re.compile(r"\bCH\d{4}CH\S{1,162}\b")


@dataclass(frozen=True)
class Finding:
    code: str
    kind: str  # "file" or "record"
    doc_ref_ids: tuple[str, ...] = ()
    fields: tuple[str, ...] = ()
    details: str = ""

    @property
    def rule(self) -> dict | None:
        return catalogue().get(self.code)

    def describe(self) -> str:
        rule = self.rule
        head = f"{self.code}"
        if rule:
            head += f" ({rule['section']}, p. {rule['page']}, {rule['status']} in aeoi)"
        refs = f" DocRefId {', '.join(self.doc_ref_ids)}" if self.doc_ref_ids else ""
        fields = f" fields {', '.join(self.fields)}" if self.fields else ""
        details = f" - {self.details}" if self.details else ""
        return f"{head}{refs}{fields}{details}"


PORTAL_ERROR_RE = re.compile(r"status\W{0,4}fehler\b|^\W*fehler\W*$", re.IGNORECASE)


@dataclass
class Outcome:
    accepted: bool | None  # None when the input does not say
    original_message_ref_id: str | None
    findings: list[Finding] = field(default_factory=list)
    source: str = ""  # "status-message-xml" or "text"
    portal_error: bool = (
        False  # portal status «Fehler»: no verdict, the file must be uploaded again
    )

    @property
    def codes(self) -> list[str]:
        return [f.code for f in self.findings]

    def should_have_been_caught(self) -> list[Finding]:
        """Findings whose rule the toolkit claims to implement: each one is a bug to fix."""
        return [f for f in self.findings if f.rule and f.rule["status"] == "implemented"]


@lru_cache(maxsize=1)
def catalogue() -> dict[str, dict]:
    return {e["code"]: e for e in json.loads(CATALOGUE.read_text(encoding="utf-8"))}


def parse_status_message(xml: str | bytes | Path) -> Outcome:
    """OECD CRS Status Message (schema 2.0) -> Outcome."""
    parser = XmlParser()
    doc = (
        parser.parse(xml, CrsstatusMessageOecd)
        if isinstance(xml, Path)
        else parser.from_string(
            xml.decode("utf-8") if isinstance(xml, bytes) else xml, CrsstatusMessageOecd
        )
    )
    status = doc.crs_status_message
    findings: list[Finding] = []
    errors = status.validation_errors
    if errors is not None:
        for fe in errors.file_error:
            findings.append(
                Finding(fe.code, "file", details=fe.details.value if fe.details else "")
            )
        for re_ in errors.record_error:
            findings.append(
                Finding(
                    re_.code,
                    "record",
                    doc_ref_ids=tuple(re_.doc_ref_idin_error),
                    fields=tuple(f.field_path for f in re_.fields_in_error),
                    details=re_.details.value if re_.details else "",
                )
            )
    accepted = None
    if status.validation_result is not None:
        accepted = status.validation_result.status.value == "Accepted"
    original = status.original_message.original_message_ref_id if status.original_message else None
    return Outcome(accepted, original, findings, source="status-message-xml")


def parse_text(text: str) -> Outcome:
    """Portal text copied by the pilot -> Outcome (codes, DocRefIds, the rest as detail)."""
    findings: list[Finding] = []
    accepted: bool | None = None
    original = None
    portal_error = False
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        low = line.lower()
        if PORTAL_ERROR_RE.search(
            line
        ):  # Benutzeranleitung: «Der Status «Fehler» erscheint, falls ein
            portal_error = (
                True  # unbekanntes Problem die Verarbeitung verhinderte ... noch einmal hochladen»
            )
            continue
        if any(
            k in low for k in ("akzeptiert", "accepted", "erfolgreich", "validierungsbestätigung")
        ):
            accepted = True if accepted is None else accepted
        if any(k in low for k in ("abgelehnt", "rejected", "zurückgewiesen", "fehlerbericht")):
            accepted = False
        codes = CODE_RE.findall(line)
        refs = tuple(DOC_REF_RE.findall(line))
        if not codes:
            if original is None and (m := MSG_REF_RE.search(line)):
                original = m.group(0)
            continue
        detail = CODE_RE.sub("", line)
        for ref in refs:
            detail = detail.replace(ref, "")
        detail = re.sub(r"\s+", " ", detail).strip(" :-|")
        for code in codes:
            kind = "file" if code.startswith("50") else "record"
            findings.append(Finding(code, kind, doc_ref_ids=refs, details=detail))
    if accepted is None and findings:
        accepted = False
    return Outcome(
        accepted, original, findings, source="text", portal_error=portal_error and accepted is None
    )


def render(outcome: Outcome) -> str:
    lines = []
    verdict = {True: "ACCEPTED", False: "REJECTED", None: "outcome unknown"}[outcome.accepted]
    lines.append(
        f"{verdict} ({outcome.source})"
        + (f" for {outcome.original_message_ref_id}" if outcome.original_message_ref_id else "")
    )
    for f in outcome.findings:
        lines.append("  " + f.describe())
    bugs = outcome.should_have_been_caught()
    if bugs:
        lines.append(
            f"  !! {len(bugs)} finding(s) concern rules the toolkit claims to enforce - report them as bugs"
        )
    return "\n".join(lines)
