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

from aeoi.crs import build as builder
from aeoi.crs import model, read_xml, xsd
from aeoi.crs.model import Version
from aeoi.estv import ids, packaging
from aeoi.messages import Msg
from aeoi.messages import text as msg_text

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

    def render(self, lang: str = "en") -> str:
        """Plain-text report; ``lang`` renders the catalogue messages (en, de)."""
        verdict = Msg("verdict_ok" if self.ok else "verdict_not_ok")
        head = Msg(
            "report_head_xml",
            verdict=verdict,
            version=self.version or "?",
            problems=Msg("n_problems", n=len(self.problems)),
            notes=Msg("n_notes", n=len(self.infos)),
        )
        lines = [head.text(lang)]
        error, note = Msg("label_error").text(lang), Msg("label_note").text(lang)
        for p in self.problems:
            lines.append(f"  {error:<6} {p.where}: {msg_text(p.message, lang)} [{p.rule}]")
        for p in self.infos:
            lines.append(f"  {note:<6} {p.where}: {msg_text(p.message, lang)}")
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
        rep.add("file", Msg("file_too_large", size=len(data)), "4.1.1")
    try:
        root = etree.fromstring(data)
    except etree.XMLSyntaxError as exc:
        rep.add("file", Msg("not_well_formed", error=str(exc)), "50007")
        return rep
    version, version_attr = read_xml.detect_version(data)
    rep.version = version
    if version is None:
        rep.add(
            "CRS_OECD",
            Msg("unknown_namespace", namespace=repr(etree.QName(root).namespace)),
            "50007",
        )
        return rep
    if version == "2.0" and version_attr == "3.0":
        # the header the Wegleitung 5.3.1 shows: 3.0 content declared in the v2 namespace.
        # Checked as 3.0 content; which header the portal accepts is open question 1.
        rep.info("CRS_OECD", Msg("header_v2_ns_v3"))
        data = builder.canonical_xml(data.decode("utf-8")).encode("utf-8")
        root = etree.fromstring(data)
        version = "3.0"
        rep.version = version
    if version_attr != version:
        rep.add(
            "CRS_OECD/@version",
            Msg("version_mismatch", attr=repr(version_attr), version=version),
            "98000",
        )
    if root.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature") is not None:
        rep.add("file", Msg("signed_xml"), "50007")
    for e in xsd.validate(data, version):
        rep.add("xsd", Msg("xsd_error", error=e), "50007")
    for el, text in _text_nodes(root):
        bad = ids.invalid_characters(text)
        if bad:
            rep.add(root.getroottree().getpath(el),
                    Msg("charset", text=repr(bad[0].text), position=bad[0].position, reason=bad[0].reason), "50005")  # fmt: skip

    # --- header and DocSpecs (readable without the domain model) ---------------------------------
    try:
        parsed = read_xml.parse(data)
    except Exception:  # noqa: BLE001 - a file outside the schema cannot be mapped
        rep.info("file", Msg("content_skipped_schema" if not rep.ok else "content_skipped_model"))
        return rep
    rep.message = parsed.message
    if parsed.transmitting_country != "CH":
        rep.add("MessageSpec/TransmittingCountry", Msg("must_be_ch"), "98002")
    if parsed.receiving_country != "CH":
        rep.add("MessageSpec/ReceivingCountry", Msg("must_be_ch"), "50012")
    if parsed.message_type != "CRS":
        rep.add("MessageSpec/MessageType", Msg("must_be_crs"), "50007")
    if parsed.corr_message_ref_id:
        rep.add("MessageSpec/CorrMessageRefId", Msg("must_not_be_used"), "80007")
    ref = parsed.message.message_ref_id or ""
    check = ids.check_message_ref_id(ref)
    for p in check.problems:
        rep.add("MessageSpec/MessageRefId", p, "50008")
    period_year = parsed.message.reporting_year
    ref_year = check.year if check.ok else period_year  # 80001 compares with the MessageRefId year
    if check.ok and not (ref_year <= period_year <= ref_year + 1):
        rep.add(
            "MessageSpec/ReportingPeriod",
            Msg(
                "period_outside", period=parsed.reporting_period, year=ref_year, year1=ref_year + 1
            ),
            "98006",
        )
    elif check.ok and period_year != ref_year:
        rep.info(
            "MessageSpec/ReportingPeriod",
            Msg("period_year_after", period=parsed.reporting_period, year=ref_year),
        )
    if not parsed.reporting_period.endswith("-12-31"):
        rep.info("MessageSpec/ReportingPeriod", Msg("period_not_dec31"))
    if parsed.crs_bodies != 1:
        rep.add("CrsBody", Msg("crs_bodies", n=parsed.crs_bodies), "98100")
    if parsed.reporting_groups != 1:
        rep.add("ReportingGroup", Msg("reporting_groups", n=parsed.reporting_groups), "60007")
    if parsed.has_sponsor:
        rep.add("ReportingGroup/Sponsor", Msg("must_not_be_used"), "60008")
    if parsed.has_intermediary:
        rep.add("ReportingGroup/Intermediary", Msg("must_not_be_used"), "60009")
    if parsed.has_pool_report:
        rep.add("ReportingGroup/PoolReport", Msg("must_not_be_used"), "60010")
    if parsed.fi_res_country_codes != ["CH"]:
        rep.add("ReportingFI/ResCountryCode", Msg("fi_res_country"), "60013")
    if parsed.fi_name_type == "OECD201":
        rep.add("ReportingFI/Name/@nameType", Msg("fi_name_type_201"), "60004")

    fi = parsed.reporting_fi_spec
    if fi.doc_type_indic not in FI_INDICS:
        rep.add(
            "ReportingFI/DocSpec/DocTypeIndic", Msg("fi_indic", indic=fi.doc_type_indic), "98101"
        )
    if fi.corr_doc_ref_id:
        rep.add("ReportingFI/DocSpec/CorrDocRefId", Msg("must_not_be_present"), "80004")
    if fi.corr_message_ref_id:
        rep.add("ReportingFI/DocSpec/CorrMessageRefId", Msg("must_not_be_present"), "80006")
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
            rep.add(f"{where}/DocRefId", Msg("doc_ref_used_twice"), "80000")
        seen.add(sp.doc_ref_id)
        is_test = sp.doc_type_indic in TEST_INDICS
        if test and not is_test:
            rep.add(
                f"{where}/DocTypeIndic",
                Msg("test_indic_in_test_file", indic=sp.doc_type_indic),
                "50011",
            )
        if not test and is_test:
            rep.add(
                f"{where}/DocTypeIndic",
                Msg("prod_indic_in_prod_file", indic=sp.doc_type_indic),
                "50010",
            )
        if i == 0:
            continue
        if sp.corr_message_ref_id:
            rep.add(f"{where}/CorrMessageRefId", Msg("must_not_be_present"), "80006")
        if sp.doc_type_indic in ("OECD0", "OECD10"):
            rep.add(f"{where}/DocTypeIndic", Msg("resend_not_allowed_ar"), "80008")
        if sp.doc_type_indic in CORR_INDICS and not sp.corr_doc_ref_id:
            rep.add(f"{where}/CorrDocRefId", Msg("corr_ref_required"), "80005")
        if sp.doc_type_indic in NEW_INDICS and sp.corr_doc_ref_id:
            rep.add(f"{where}/CorrDocRefId", Msg("corr_ref_not_allowed_new"), "80005")
        if sp.corr_doc_ref_id:
            if sp.corr_doc_ref_id in corr_seen:
                rep.add(f"{where}/CorrDocRefId", Msg("corrected_twice"), "80011")
            corr_seen.add(sp.corr_doc_ref_id)
        if indic == "CRS701" and sp.doc_type_indic in CORR_INDICS:
            rep.add(f"{where}/DocTypeIndic", Msg("corrections_in_crs701"), "80010")
        if indic == "CRS702" and sp.doc_type_indic in NEW_INDICS:
            rep.add(f"{where}/DocTypeIndic", Msg("new_in_crs702"), "80010")

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
        rep.info("file", Msg("transitional_present"))
    return rep
