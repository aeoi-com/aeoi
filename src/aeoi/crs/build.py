"""Domain model -> OECD CRS XML (schema 2.0 or 3.0) for submission FI -> ESTV.

The two generated schema packages have the same class names; the builder picks one by version.
For 3.0 the document is written in the OECD namespace ``urn:oecd:ties:crs:v3`` by default;
``header="wegleitung"`` writes the header the ESTV Technische Wegleitung 5.3.1 shows instead
(``xmlns:crs="urn:oecd:ties:crs:v2"`` with ``version="3.0"``) - same content, only the namespace
declaration differs, so a pilot can try the other variant if the portal rejects the first (see
docs/OPEN-QUESTIONS.md, item 1). :func:`canonical_xml` maps the variant back for schema checks. The XML is never signed (Wegleitung 5.2, error 50007).

Message header (Wegleitung 5.3.2): SendingCompanyIN = ESTV-ID, TransmittingCountry = CH,
ReceivingCountry = CH, MessageType = CRS, MessageRefId = CH<year>CH<uuid>, ReportingPeriod =
<year>-12-31, Timestamp = now (UTC). DocSpec: OECD1 (new) or OECD11 (test); DocRefId =
CH<year>CH<uuid> unless given; ReportingFI is never corrected or deleted (80004).
"""

from __future__ import annotations

import datetime as dt
import importlib
import pkgutil
from dataclasses import dataclass
from decimal import Decimal
from types import ModuleType, SimpleNamespace

from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.models.datatype import XmlDate, XmlDateTime

from aeoi.crs import checksums
from aeoi.crs.model import TDT_PREFIX, Account, Address, Message, Organisation, Person, Version
from aeoi.estv import ids

HEADERS = ("oecd", "wegleitung")
V3_DECL = 'xmlns:crs="urn:oecd:ties:crs:v3"'
WEGLEITUNG_DECL = 'xmlns:crs="urn:oecd:ties:crs:v2"'


def canonical_xml(xml: str) -> str:
    """The OECD-conformant form of a 3.0 file written with the Wegleitung header."""
    if 'version="3.0"' in xml[:600] and WEGLEITUNG_DECL in xml[:600]:
        return xml.replace(WEGLEITUNG_DECL, V3_DECL, 1)
    return xml


def is_wegleitung_header(xml: str) -> bool:
    return 'version="3.0"' in xml[:600] and WEGLEITUNG_DECL in xml[:600]


NS = {
    "2.0": {
        "crs": "urn:oecd:ties:crs:v2",
        "cfc": "urn:oecd:ties:commontypesfatcacrs:v2",
        "stf": "urn:oecd:ties:crsstf:v5",
    },
    "3.0": {
        "crs": "urn:oecd:ties:crs:v3",
        "cfc": "urn:oecd:ties:commontypesfatcacrs:v2",
        "stf": "urn:oecd:ties:crsstf:v5",
    },
}


def schema_module(version: Version) -> SimpleNamespace:
    """All generated classes of one schema version, merged into a single namespace.

    The xsdata package splits classes by source XSD (CrsXML, CommonTypesFatcaCrs, oecdcrstypes,
    isocrstypes); the builder does not care which file a type came from.
    """
    if version == "2.0":
        package = "aeoi.schemas.crs_v2"
    elif version == "3.0":
        package = "aeoi.schemas.crs_v3"
    else:
        raise ValueError(f"unsupported CRS schema version {version!r}")
    merged: dict[str, object] = {}
    pkg = importlib.import_module(package)
    for info in pkgutil.iter_modules(pkg.__path__):
        mod: ModuleType = importlib.import_module(f"{package}.{info.name}")
        for name in dir(mod):
            if name[0].isupper() and name not in merged:
                merged[name] = getattr(mod, name)
    return SimpleNamespace(**merged)


TEST_INDIC = {"OECD0": "OECD10", "OECD1": "OECD11", "OECD2": "OECD12", "OECD3": "OECD13"}


@dataclass(frozen=True)
class RecordPlan:
    """How one account goes into the message (Wegleitung Ziffer 6).

    ``doc_type_indic``: OECD1 new, OECD2 correction, OECD3 deletion (test variants are derived
    from the ``test`` flag of the build). ``corr_doc_ref_id`` is mandatory for OECD2/OECD3 and
    must be the DocRefId of the last valid link of the record's chain (80002, 80003, 98103).
    """

    key: str
    doc_ref_id: str
    doc_type_indic: str = "OECD1"
    corr_doc_ref_id: str | None = None


@dataclass(frozen=True)
class FiPlan:
    """ReportingFI DocSpec: OECD1 with a new DocRefId, or OECD0 resend with the DocRefId already
    sent (6.4.1, 6.4.6; 98102). The ReportingFI is never corrected or deleted (80004)."""

    doc_ref_id: str
    resend: bool = False


@dataclass(frozen=True)
class BuildResult:
    xml: str
    version: Version
    message_ref_id: str
    doc_ref_ids: dict[str, str]  # account key -> DocRefId
    reporting_fi_doc_ref_id: str
    records: tuple[RecordPlan, ...] = ()
    fi_plan: FiPlan | None = None
    header: str = "oecd"  # "oecd" (namespace v3) or "wegleitung" (v2 declaration, 3.0 content)


def _address(m: SimpleNamespace, a: Address):
    address_fix = m.AddressFixType(
        street=a.street,
        building_identifier=a.building_identifier,
        suite_identifier=a.suite_identifier,
        floor_identifier=a.floor_identifier,
        district_name=a.district_name,
        pob=a.pob,
        post_code=a.post_code,
        city=a.city,
        country_subentity=a.country_subentity,
    )
    return m.AddressType(
        country_code=m.CountryCodeType(a.country),
        address_fix=address_fix,
        address_free=a.address_free,
        legal_address_type=(
            m.OecdlegalAddressTypeEnumType(a.legal_address_type) if a.legal_address_type else None
        ),
    )


def _person(m: SimpleNamespace, p: Person):
    name = m.NamePersonType(
        first_name=m.NamePersonType.FirstName(value=p.first_name),
        last_name=m.NamePersonType.LastName(value=p.last_name),
        middle_name=[m.NamePersonType.MiddleName(value=p.middle_name)] if p.middle_name else [],
        name_type=m.OecdnameTypeEnumType(p.name_type) if p.name_type else None,
    )
    birth = None
    if p.birth_date or p.birth_city or p.birth_country:
        country = (
            m.PersonPartyType.BirthInfo.CountryInfo(country_code=m.CountryCodeType(p.birth_country))
            if p.birth_country
            else None
        )
        birth = m.PersonPartyType.BirthInfo(
            birth_date=XmlDate.from_date(p.birth_date) if p.birth_date else None,
            city=p.birth_city,
            country_info=country,
        )
    return m.PersonPartyType(
        res_country_code=[m.CountryCodeType(c) for c in p.residence_countries],
        tin=[
            m.TinType(
                value=t.value, issued_by=m.CountryCodeType(t.issued_by) if t.issued_by else None
            )
            for t in p.tins
        ],
        name=[name],
        address=[_address(m, p.address)],
        nationality=[m.CountryCodeType(c) for c in p.nationalities],
        birth_info=birth,
    )


def _organisation(m: SimpleNamespace, o: Organisation):
    return m.OrganisationPartyType(
        res_country_code=[m.CountryCodeType(c) for c in o.residence_countries],
        in_value=[
            m.OrganisationInType(
                value=t.value, issued_by=m.CountryCodeType(t.issued_by) if t.issued_by else None
            )
            for t in o.ins
        ],
        name=[
            m.NameOrganisationType(
                value=o.name, name_type=m.OecdnameTypeEnumType(o.name_type) if o.name_type else None
            )
        ],
        address=[_address(m, o.address)],
    )


def _doc_spec(
    m: SimpleNamespace,
    doc_ref_id: str,
    *,
    test: bool,
    doc_type_indic: str = "OECD1",
    corr_doc_ref_id: str | None = None,
):
    indic = TEST_INDIC[doc_type_indic] if test else doc_type_indic
    return m.DocSpecType(
        doc_type_indic=m.OecddocTypeIndicEnumType(indic),
        doc_ref_id=doc_ref_id,
        corr_doc_ref_id=corr_doc_ref_id,
    )


def _account_report(
    m: SimpleNamespace, acc: Account, version: Version, plan: RecordPlan, *, test: bool
):
    if acc.holder_person is not None:
        holder_kwargs = {"individual": _person(m, acc.holder_person)}
    else:
        assert acc.holder_organisation is not None
        holder_kwargs = {
            "organisation": _organisation(m, acc.holder_organisation),
            "acct_holder_type": m.CrsAcctHolderTypeEnumType(
                acc.holder_organisation.acct_holder_type
            ),
        }
    if version == "3.0":
        holder_kwargs["self_cert"] = m.CrsSelfCertEnumType(acc.self_cert)
        holder_kwargs["equity_interest_type"] = [
            m.EquityInterestTypeEnumType(e) for e in acc.equity_interest_types
        ]
    holder = m.AccountHolderType(**holder_kwargs)

    cps = []
    for cp in acc.controlling_persons:
        kwargs = {"individual": _person(m, cp.person)}
        if version == "3.0":
            kwargs["ctrlg_person_type"] = [
                m.CrsCtrlgPersonTypeEnumType(t) for t in cp.ctrlg_person_types
            ]
            kwargs["self_cert"] = m.CrsSelfCertforCtrlgPersonTypeEnumType(cp.self_cert)
        elif cp.ctrlg_person_types:
            kwargs["ctrlg_person_type"] = m.CrsCtrlgPersonTypeEnumType(cp.ctrlg_person_types[0])
        cps.append(m.ControllingPersonType(**kwargs))

    kwargs = {
        "doc_spec": _doc_spec(
            m,
            plan.doc_ref_id,
            test=test,
            doc_type_indic=plan.doc_type_indic,
            corr_doc_ref_id=plan.corr_doc_ref_id,
        ),
        "account_number": m.FiaccountNumberType(
            value=account_number_for_xml(acc),
            acct_number_type=(
                m.AcctNumberTypeEnumType(acc.account_number_type)
                if acc.account_number_type
                else None
            ),
            undocumented_account=acc.undocumented or None,
            closed_account=acc.closed or None,
            dormant_account=acc.dormant or None,
        ),
        "account_holder": holder,
        "controlling_person": cps,
        "account_balance": m.MonAmntType(
            value=_money(acc.balance), curr_code=m.CurrCodeType(acc.currency)
        ),
        "payment": [
            m.PaymentType(
                type_value=m.CrsPaymentTypeEnumType(p.payment_type),
                payment_amnt=m.MonAmntType(
                    value=_money(p.amount), curr_code=m.CurrCodeType(p.currency)
                ),
            )
            for p in acc.payments
        ],
    }
    if version == "3.0":
        kwargs["ddprocedure"] = m.OpeningDateEnumType(acc.dd_procedure)
        kwargs["account_type"] = m.CrsAccountTypeEnumType(acc.account_type)
        if acc.joint_account_number is not None:
            kwargs["joint_account"] = m.CorrectableAccountReportType.JointAccount(
                number=acc.joint_account_number
            )
    return m.CorrectableAccountReportType(**kwargs)


def account_number_for_xml(acc: Account) -> str:
    """IBAN and ISIN are written normalised (no spaces or hyphens, upper case): the ESTV checks
    '2 Buchstaben & 2 Ziffern & max. 30 Buchstaben oder Ziffern' on the raw value (60000/60001),
    while bank exports usually space the IBAN."""
    if acc.account_number_type in ("OECD601", "OECD603"):
        return checksums.normalise(acc.account_number)
    return acc.account_number


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def build(
    msg: Message,
    version: Version,
    *,
    test: bool = False,
    now: dt.datetime | None = None,
    records: list[RecordPlan] | None = None,
    fi_plan: FiPlan | None = None,
    header: str = "oecd",
) -> BuildResult:
    """Render the message as CRS XML. Run :func:`aeoi.crs.model.check_message` first.

    Without ``records`` every account is a new record (OECD1) with its ``doc_ref_id`` or a
    generated one; without ``fi_plan`` the ReportingFI is OECD1 with a new DocRefId. The
    submission registry supplies both for follow-up and correction messages.
    """
    m = schema_module(version)
    now = now or dt.datetime.now(dt.UTC)
    year = msg.reporting_year
    message_ref_id = msg.message_ref_id or ids.message_ref_id(year)
    fi = msg.reporting_fi
    fi_plan = fi_plan or FiPlan(ids.doc_ref_id(year))
    fi_doc_ref_id = fi_plan.doc_ref_id
    plans = {p.key: p for p in records} if records is not None else {}
    if records is not None:
        missing = [a.key for a in msg.accounts if a.key not in plans]
        if missing:
            raise ValueError(f"no record plan for accounts {missing}")

    reporting_fi = m.CorrectableOrganisationPartyType(
        res_country_code=[m.CountryCodeType("CH")],
        in_value=(
            [m.OrganisationInType(value=fi.uid, issued_by=m.CountryCodeType("CH"))]
            if fi.uid
            else []
        ),  # IN only when the FI has a UID (70015)
        name=[
            m.NameOrganisationType(
                value=(TDT_PREFIX if fi.trustee_documented_trust else "") + fi.name,
                name_type=m.OecdnameTypeEnumType("OECD207"),
            )
        ],  # trustee-documented trust: "TDT=" + trust name (Wegleitung 5.3.4)
        address=[_address(m, fi.address)],
        doc_spec=_doc_spec(
            m, fi_doc_ref_id, test=test, doc_type_indic="OECD0" if fi_plan.resend else "OECD1"
        ),
    )
    doc_ref_ids: dict[str, str] = {}
    reports = []
    used: list[RecordPlan] = []
    for acc in msg.accounts:
        plan = plans.get(acc.key) or RecordPlan(acc.key, acc.doc_ref_id or ids.doc_ref_id(year))
        doc_ref_ids[acc.key] = plan.doc_ref_id
        used.append(plan)
        reports.append(_account_report(m, acc, version, plan, test=test))

    doc = m.CrsOecd(
        version=version,
        message_spec=m.MessageSpecType(
            sending_company_in=fi.estv_id,
            transmitting_country=m.CountryCodeType("CH"),
            receiving_country=m.CountryCodeType("CH"),
            message_type=m.MessageTypeEnumType("CRS"),
            message_ref_id=message_ref_id,
            message_type_indic=m.CrsMessageTypeIndicEnumType(msg.message_type_indic),
            reporting_period=XmlDate(year, 12, 31),
            timestamp=XmlDateTime.from_datetime(now.replace(microsecond=0)),
        ),
        crs_body=[
            m.CrsBodyType(
                reporting_fi=reporting_fi,
                reporting_group=[m.CrsBodyType.ReportingGroup(account_report=reports)],
            )
        ],
    )
    xml = XmlSerializer(config=SerializerConfig(indent="  ", encoding="UTF-8")).render(
        doc, ns_map=NS[version]
    )
    if header not in HEADERS:
        raise ValueError(f"header must be one of {HEADERS}")
    if header == "wegleitung" and version == "3.0":
        xml = xml.replace(V3_DECL, WEGLEITUNG_DECL, 1)
    return BuildResult(
        xml, version, message_ref_id, doc_ref_ids, fi_doc_ref_id, tuple(used), fi_plan, header
    )
