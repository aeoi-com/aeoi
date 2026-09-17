"""Validate a CRS XML file the way the ESTV portal will, before it is packaged or uploaded.

Works on any file (produced by this toolkit or another one): the OECD XSD (50007), the header
and DocSpec rules of the Technische Wegleitung readable from the file itself, the character set
(50005), the size limits, and - through :func:`aeoi.crs.read_xml.parse` and
:func:`aeoi.crs.model.check_message` - the content rules (partner states, checksums, cross-field
rules). Rules that need the history of earlier messages are the registry's job.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

from aeoi.crs import model, read_xml, xsd
from aeoi.crs.model import Version
from aeoi.estv import ids, packaging

WEGLEITUNG_3_0_HEADER_NS = "urn:oecd:ties:crs:v2"
NEW_INDICS = {"OECD1", "OECD11"}
CORR_INDICS = {"OECD2", "OECD3", "OECD12", "OECD13"}
TEST_INDICS = {"OECD10", "OECD11", "OECD12", "OECD13"}
FI_INDICS = {"OECD0", "OECD1", "OECD10", "OECD11"}


@dataclass
class ValidationReport:
    version: Version | None = None
    problems: list[model.Problem] = field(default_factory=list)
    infos: list[model.Problem] = field(default_factory=list)
    message: model.Message | None = None  # the parsed content, when the file could be read

    @property
    def ok(self) -> bool:
        return not self.problems

    def add(self, where: str, message: str, rule: str = "") -> None:
        self.problems.append(model.Problem(where, message, rule))

    def info(self, where: str, message: str) -> None:
        self.infos.append(model.Problem(where, message, "info"))

    def render(self) -> str:
        head = (
            f"{'OK' if self.ok else 'NOT OK'}: CRS {self.version or '?'}, "
            f"{len(self.problems)} problem(s), {len(self.infos)} note(s)"
        )
        lines = [head]
        for p in self.problems:
            lines.append(f"  error  {p.where}: {p.message} [{p.rule}]")
        for p in self.infos:
            lines.append(f"  note   {p.where}: {p.message}")
        return "\n".join(lines)


def _text_nodes(root: etree._Element):
    for el in root.iter():
        if el.text and el.text.strip():
            yield el, el.text


def validate_file(
    path: str | Path,
    *,
    test: bool | None = None,
    today: dt.date | None = None,
) -> ValidationReport:
    path = Path(path)
    data = path.read_bytes()
    rep = ValidationReport()
    if test is None:
        test = path.name.lower().startswith(packaging.TEST_PREFIX)

    # --- file level ---------------------------------------------------------------------------
    if len(data) > packaging.MAX_XML_BYTES:
        rep.add("file", f"{len(data)} bytes, above the 100 MB limit; split the message", "4.1.1")
    try:
        root = etree.fromstring(data)
    except etree.XMLSyntaxError as exc:
        rep.add("file", f"not well-formed XML: {exc}", "50007")
        return rep
    version, version_attr = read_xml.detect_version(data)
    rep.version = version
    if version is None:
        rep.add("CRS_OECD", f"unknown root namespace {etree.QName(root).namespace!r}", "50007")
        return rep
    if version == "2.0" and version_attr == "3.0":
        rep.add("CRS_OECD", "namespace urn:oecd:ties:crs:v2 with version=\"3.0\": this is the "
                "header shown in the Wegleitung 5.3.1, but the OECD 3.0 schema declares "
                "urn:oecd:ties:crs:v3; the file matches neither schema (open question 1)",
                "98000")  # fmt: skip
        return rep
    if version_attr != version:
        rep.add("CRS_OECD/@version",
                f"version attribute {version_attr!r} does not match the namespace of schema "
                f"{version}", "98000")  # fmt: skip
    if root.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature") is not None:
        rep.add("file", "the XML is signed; the ESTV rejects signed files", "50007")
    for e in xsd.validate(data, version):
        rep.add("xsd", e, "50007")
    for el, text in _text_nodes(root):
        bad = ids.invalid_characters(text)
        if bad:
            rep.add(root.getroottree().getpath(el),
                    f"{bad[0].text!r} at position {bad[0].position}: {bad[0].reason}", "50005")  # fmt: skip

    # --- header and DocSpecs (readable without the domain model) ---------------------------------
    try:
        parsed = read_xml.parse(data)
    except Exception:  # noqa: BLE001 - a file outside the schema cannot be mapped
        rep.info(
            "file",
            "content checks skipped: the file does not follow the schema (see the 50007 errors)"
            if not rep.ok
            else "content checks skipped: the file could not be read into the model",
        )
        return rep
    rep.message = parsed.message
    if parsed.transmitting_country != "CH":
        rep.add("MessageSpec/TransmittingCountry", "must be CH", "98002")
    if parsed.receiving_country != "CH":
        rep.add("MessageSpec/ReceivingCountry", "must be CH", "50012")
    if parsed.message_type != "CRS":
        rep.add("MessageSpec/MessageType", "must be CRS", "50007")
    if parsed.corr_message_ref_id:
        rep.add("MessageSpec/CorrMessageRefId", "must not be used", "80007")
    ref = parsed.message.message_ref_id or ""
    check = ids.check_message_ref_id(ref)
    for p in check.problems:
        rep.add("MessageSpec/MessageRefId", p, "50008")
    period_year = parsed.message.reporting_year
    ref_year = check.year if check.ok else period_year  # 80001 compares with the MessageRefId year
    if check.ok and not (ref_year <= period_year <= ref_year + 1):
        rep.add(
            "MessageSpec/ReportingPeriod",
            f"{parsed.reporting_period} is outside 1.1.{ref_year} - 31.12.{ref_year + 1} "
            f"(MessageRefId year {ref_year})",
            "98006",
        )
    elif check.ok and period_year != ref_year:
        rep.info(
            "MessageSpec/ReportingPeriod",
            f"{parsed.reporting_period} is in the year after the MessageRefId year {ref_year}; "
            "allowed by 98006, unusual for a Swiss FI",
        )
    if not parsed.reporting_period.endswith("-12-31"):
        rep.info("MessageSpec/ReportingPeriod", "not 31 December; unusual for a Swiss FI")
    if parsed.crs_bodies != 1:
        rep.add("CrsBody", f"{parsed.crs_bodies} CrsBody elements; exactly one", "98100")
    if parsed.reporting_groups != 1:
        rep.add("ReportingGroup", f"{parsed.reporting_groups} groups; exactly one", "60007")
    if parsed.has_sponsor:
        rep.add("ReportingGroup/Sponsor", "must not be used", "60008")
    if parsed.has_intermediary:
        rep.add("ReportingGroup/Intermediary", "must not be used", "60009")
    if parsed.has_pool_report:
        rep.add("ReportingGroup/PoolReport", "must not be used", "60010")
    if parsed.fi_res_country_codes != ["CH"]:
        rep.add("ReportingFI/ResCountryCode", "must be exactly CH", "60013")
    if parsed.fi_name_type == "OECD201":
        rep.add("ReportingFI/Name/@nameType", "OECD201 is not allowed", "60004")

    fi = parsed.reporting_fi_spec
    if fi.doc_type_indic not in FI_INDICS:
        rep.add("ReportingFI/DocSpec/DocTypeIndic",
                f"{fi.doc_type_indic}: the ReportingFI is never corrected or deleted", "98101")  # fmt: skip
    if fi.corr_doc_ref_id:
        rep.add("ReportingFI/DocSpec/CorrDocRefId", "must not be present", "80004")
    if fi.corr_message_ref_id:
        rep.add("ReportingFI/DocSpec/CorrMessageRefId", "must not be present", "80006")
    specs = [fi, *parsed.account_specs]
    seen: set[str] = set()
    corr_seen: set[str] = set()
    indic = parsed.message.message_type_indic
    for i, sp in enumerate(specs):
        where = "ReportingFI/DocSpec" if i == 0 else f"AccountReport[{i}]/DocSpec"
        c = ids.check_doc_ref_id(sp.doc_ref_id, message_year=ref_year)
        for p in c.problems:
            rep.add(f"{where}/DocRefId", p, "80001")
        if sp.doc_ref_id in seen and sp.doc_type_indic not in ("OECD0", "OECD10"):
            rep.add(f"{where}/DocRefId", "used twice in this file", "80000")
        seen.add(sp.doc_ref_id)
        is_test = sp.doc_type_indic in TEST_INDICS
        if test and not is_test:
            rep.add(f"{where}/DocTypeIndic",
                    f"{sp.doc_type_indic} in a test file (name starts with Test)", "50011")  # fmt: skip
        if not test and is_test:
            rep.add(f"{where}/DocTypeIndic",
                    f"{sp.doc_type_indic} in a productive file", "50010")  # fmt: skip
        if i == 0:
            continue
        if sp.corr_message_ref_id:
            rep.add(f"{where}/CorrMessageRefId", "must not be present", "80006")
        if sp.doc_type_indic in ("OECD0", "OECD10"):
            rep.add(
                f"{where}/DocTypeIndic", "Resend Data is not allowed for AccountReports", "80008"
            )
        if sp.doc_type_indic in CORR_INDICS and not sp.corr_doc_ref_id:
            rep.add(f"{where}/CorrDocRefId", "required for corrections and deletions", "80005")
        if sp.doc_type_indic in NEW_INDICS and sp.corr_doc_ref_id:
            rep.add(f"{where}/CorrDocRefId", "not allowed on a new record", "80005")
        if sp.corr_doc_ref_id:
            if sp.corr_doc_ref_id in corr_seen:
                rep.add(
                    f"{where}/CorrDocRefId", "the same record corrected twice in one file", "80011"
                )
            corr_seen.add(sp.corr_doc_ref_id)
        if indic == "CRS701" and sp.doc_type_indic in CORR_INDICS:
            rep.add(f"{where}/DocTypeIndic", "corrections in a CRS701 message", "80010")
        if indic == "CRS702" and sp.doc_type_indic in NEW_INDICS:
            rep.add(f"{where}/DocTypeIndic", "new records in a CRS702 message", "80010")

    # --- content rules through the domain model ----------------------------------------------------
    content = model.check_message(
        parsed.message, version, today=today, correction=indic == "CRS702"
    )
    for p in content.problems:
        if p.rule == "info":
            rep.info(p.where, p.message)
        elif p.rule == "50005" or (p.rule == "80000" and p.where.startswith("Accounts[doc_ref_id")):
            continue  # already reported above from the XML nodes / DocSpecs
        else:
            rep.add(p.where, p.message, p.rule)
    if version == "3.0" and re.search(
        r"CRS(800|900|1000|1100|1200)\b", data.decode("utf-8", "ignore")
    ):
        rep.info("file", "transitional 'not reported' values present (open question 3)")
    return rep
