"""Read a CRS XML file (2.0 or 3.0) back into the domain model, with its DocSpec metadata.

The inverse of :mod:`aeoi.crs.build`. It is used by ``aeoi crs validate`` to apply the content
rules of :func:`aeoi.crs.model.check_message` to a file produced by any tool, and it keeps the
identifiers (MessageRefId, DocRefIds, DocTypeIndics, CorrDocRefIds) for the structural checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from lxml import etree
from xsdata.formats.dataclass.parsers import XmlParser

from aeoi.crs.build import schema_module
from aeoi.crs.model import (
    Account,
    Address,
    ControllingPerson,
    Message,
    Organisation,
    Payment,
    Person,
    ReportingFI,
    Tin,
    Version,
)

NAMESPACES = {"urn:oecd:ties:crs:v2": "2.0", "urn:oecd:ties:crs:v3": "3.0"}


@dataclass(frozen=True)
class DocSpecInfo:
    doc_type_indic: str
    doc_ref_id: str
    corr_doc_ref_id: str | None
    corr_message_ref_id: str | None


@dataclass
class ParsedFile:
    version: Version  # from the root namespace
    version_attribute: str | None  # the version="..." attribute as written
    message: Message
    reporting_fi_spec: DocSpecInfo
    account_specs: list[DocSpecInfo] = field(default_factory=list)
    sending_company_in: str | None = None
    transmitting_country: str = ""
    receiving_country: str = ""
    message_type: str = ""
    corr_message_ref_id: list[str] = field(default_factory=list)
    reporting_period: str = ""
    timestamp: str = ""
    crs_bodies: int = 1
    reporting_groups: int = 1
    has_sponsor: bool = False
    has_intermediary: bool = False
    has_pool_report: bool = False
    fi_res_country_codes: list[str] = field(default_factory=list)
    fi_name_type: str | None = None
    fi_in_issued_by: str | None = None


def detect_version(xml: bytes) -> tuple[Version | None, str | None]:
    root = etree.fromstring(xml)
    ns = etree.QName(root).namespace
    return NAMESPACES.get(ns or ""), root.get("version")


def _str(v) -> str | None:
    if v is None:
        return None
    return v.value if hasattr(v, "value") else str(v)


def _address(a) -> Address:
    fix = a.address_fix
    return Address(
        country=_str(a.country_code) or "",
        city=(fix.city if fix else "") or "",
        street=fix.street if fix else None,
        building_identifier=fix.building_identifier if fix else None,
        suite_identifier=fix.suite_identifier if fix else None,
        floor_identifier=fix.floor_identifier if fix else None,
        district_name=fix.district_name if fix else None,
        pob=fix.pob if fix else None,
        post_code=fix.post_code if fix else None,
        country_subentity=fix.country_subentity if fix else None,
        address_free=a.address_free,
        legal_address_type=_str(a.legal_address_type),
    )


def _person(p) -> Person:
    name = p.name[0]
    birth = p.birth_info
    return Person(
        first_name=name.first_name.value,
        last_name=name.last_name.value,
        middle_name=name.middle_name[0].value if name.middle_name else None,
        name_type=_str(name.name_type),
        birth_date=birth.birth_date.to_date() if birth and birth.birth_date else None,
        birth_city=birth.city if birth else None,
        birth_country=(
            _str(birth.country_info.country_code) if birth and birth.country_info else None
        ),
        residence_countries=[_str(c) for c in p.res_country_code],
        tins=[Tin(value=t.value, issued_by=_str(t.issued_by)) for t in p.tin],
        nationalities=[_str(c) for c in p.nationality],
        address=_address(p.address[0]) if p.address else Address(country="", city=""),
    )


def _organisation(o, acct_holder_type: str) -> Organisation:
    return Organisation(
        name=o.name[0].value,
        name_type=_str(o.name[0].name_type),
        acct_holder_type=acct_holder_type,
        residence_countries=[_str(c) for c in o.res_country_code],
        ins=[Tin(value=t.value, issued_by=_str(t.issued_by)) for t in o.in_value],
        address=_address(o.address[0]) if o.address else Address(country="", city=""),
    )


def _spec(d) -> DocSpecInfo:
    return DocSpecInfo(
        doc_type_indic=_str(d.doc_type_indic) or "",
        doc_ref_id=d.doc_ref_id,
        corr_doc_ref_id=d.corr_doc_ref_id,
        corr_message_ref_id=d.corr_message_ref_id,
    )


def parse(xml: bytes | str | Path) -> ParsedFile:
    data = (
        xml.read_bytes()
        if isinstance(xml, Path)
        else (xml.encode() if isinstance(xml, str) else xml)
    )
    version, version_attr = detect_version(data)
    if version is None:
        raise ValueError("root element is not a CRS_OECD document of schema 2.0 or 3.0")
    m = schema_module(version)
    doc = XmlParser().from_bytes(data, m.CrsOecd)
    spec = doc.message_spec
    body = doc.crs_body[0] if doc.crs_body else None
    if body is None:
        raise ValueError("no CrsBody in the file")
    fi = body.reporting_fi
    group = body.reporting_group[0] if body.reporting_group else None

    accounts: list[Account] = []
    specs: list[DocSpecInfo] = []
    for i, ar in enumerate(group.account_report if group else []):
        holder = ar.account_holder
        person = organisation = None
        if holder.individual is not None:
            person = _person(holder.individual)
        else:
            organisation = _organisation(holder.organisation, _str(holder.acct_holder_type) or "")
        cps = []
        for cp in ar.controlling_person:
            types = cp.ctrlg_person_type
            if not isinstance(types, list):
                types = [types] if types else []
            cps.append(
                ControllingPerson(
                    person=_person(cp.individual),
                    ctrlg_person_types=[_str(t) for t in types],
                    self_cert=_str(getattr(cp, "self_cert", None)),
                )
            )
        joint = getattr(ar, "joint_account", None)
        accounts.append(
            Account(
                key=f"AR{i + 1}",
                doc_ref_id=ar.doc_spec.doc_ref_id,
                account_number=ar.account_number.value,
                account_number_type=_str(ar.account_number.acct_number_type),
                undocumented=bool(ar.account_number.undocumented_account),
                closed=bool(ar.account_number.closed_account),
                dormant=bool(ar.account_number.dormant_account),
                holder_person=person,
                holder_organisation=organisation,
                controlling_persons=cps,
                balance=Decimal(ar.account_balance.value),
                currency=_str(ar.account_balance.curr_code) or "",
                payments=[
                    Payment(
                        payment_type=_str(p.type_value) or "",
                        amount=Decimal(p.payment_amnt.value),
                        currency=_str(p.payment_amnt.curr_code) or "",
                    )
                    for p in ar.payment
                ],
                self_cert=_str(getattr(holder, "self_cert", None)),
                dd_procedure=_str(getattr(ar, "ddprocedure", None)),
                account_type=_str(getattr(ar, "account_type", None)),
                joint_account_number=joint.number if joint is not None else None,
                equity_interest_types=[
                    _str(e) for e in getattr(holder, "equity_interest_type", [])
                ],
            )
        )
        specs.append(_spec(ar.doc_spec))

    fi_name = fi.name[0].value if fi.name else ""
    tdt = fi_name.upper().startswith("TDT=")
    message = Message(
        reporting_fi=ReportingFI(
            estv_id=spec.sending_company_in or "",
            uid=fi.in_value[0].value if fi.in_value else None,
            name=fi_name[4:] if tdt else fi_name,
            trustee_documented_trust=tdt,
            address=_address(fi.address[0]) if fi.address else Address(country="", city=""),
        ),
        reporting_year=spec.reporting_period.year,
        accounts=accounts,
        message_type_indic=_str(spec.message_type_indic) or "",
        message_ref_id=spec.message_ref_id,
    )
    return ParsedFile(
        version=version,
        version_attribute=version_attr,
        message=message,
        reporting_fi_spec=_spec(fi.doc_spec),
        account_specs=specs,
        sending_company_in=spec.sending_company_in,
        transmitting_country=_str(spec.transmitting_country) or "",
        receiving_country=_str(spec.receiving_country) or "",
        message_type=_str(spec.message_type) or "",
        corr_message_ref_id=list(spec.corr_message_ref_id),
        reporting_period=str(spec.reporting_period),
        timestamp=str(spec.timestamp),
        crs_bodies=len(doc.crs_body),
        reporting_groups=len(body.reporting_group),
        has_sponsor=bool(group and group.sponsor),
        has_intermediary=bool(group and group.intermediary),
        has_pool_report=bool(group and group.pool_report),
        fi_res_country_codes=[_str(c) for c in fi.res_country_code],
        fi_name_type=_str(fi.name[0].name_type) if fi.name else None,
        fi_in_issued_by=_str(fi.in_value[0].issued_by) if fi.in_value else None,
    )
