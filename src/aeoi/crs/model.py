"""Domain model of a CRS message between a Swiss reporting FI and the ESTV.

The model is version-neutral: it holds every field of CRS 3.0; :func:`check_message` says what is
missing or inconsistent for a given schema version (2.0 or 3.0) and returns *talking* problems
with a location (sheet, row, column) instead of raising on the first one.

Rules referenced by number come from the ESTV Technische Wegleitung (09.2026); the XSD
requirements come from ``CrsXML_v2.0.xsd`` / ``CrsXML_v3.0.xsd``. Rules that need data outside
the message (partner-state list, IBAN/ISIN checksums, sent DocRefIds) belong to the rule engine.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from aeoi.crs import codes
from aeoi.estv import ids

Version = Literal["2.0", "3.0"]
COUNTRY_RE = re.compile(r"^[A-Z]{2}$")
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
# The Wegleitung does not define the ESTV-ID format; 052.0000.0000 is its example. Rule 98001
# compares the value with the one registered in the portal, so another shape is only a warning.
ESTV_ID_RE = re.compile(r"^\d{3}\.\d{4}\.\d{4}$")
UID_RE = re.compile(r"^CHE-\d{3}\.\d{3}\.\d{3}$")
TDT_PREFIX = "TDT="


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Address(Strict):
    country: str
    city: str
    street: str | None = None
    building_identifier: str | None = None
    suite_identifier: str | None = None
    floor_identifier: str | None = None
    district_name: str | None = None
    pob: str | None = None
    post_code: str | None = None
    country_subentity: str | None = None
    address_free: str | None = None
    legal_address_type: str | None = None


class Tin(Strict):
    value: str
    issued_by: str | None = None


class Person(Strict):
    """A natural person: account holder (Individual) or controlling person."""

    first_name: str
    last_name: str
    middle_name: str | None = None
    name_type: str | None = None
    birth_date: dt.date | None = None
    birth_city: str | None = None
    birth_country: str | None = None
    residence_countries: list[str] = Field(default_factory=list)
    tins: list[Tin] = Field(default_factory=list)
    nationalities: list[str] = Field(default_factory=list)
    address: Address


class Organisation(Strict):
    name: str
    name_type: str | None = None
    acct_holder_type: str  # CRS101 / CRS102 / CRS103
    residence_countries: list[str] = Field(default_factory=list)
    ins: list[Tin] = Field(default_factory=list)  # IN elements (issuedBy optional)
    address: Address


class ControllingPerson(Strict):
    person: Person
    ctrlg_person_types: list[str] = Field(default_factory=list)  # 3.0: 1..n; 2.0: 0..1
    self_cert: str | None = None  # 3.0: CRS1001/CRS1002 mandatory


class Payment(Strict):
    payment_type: str  # CRS501-504
    amount: Decimal
    currency: str


class Account(Strict):
    key: str  # row identifier in the flat input; not written to the XML
    doc_ref_id: str | None = None  # generated when empty
    account_number: str  # or NANUM
    account_number_type: str | None = None  # OECD601-606
    undocumented: bool = False
    closed: bool = False
    dormant: bool = False
    holder_person: Person | None = None
    holder_organisation: Organisation | None = None
    controlling_persons: list[ControllingPerson] = Field(default_factory=list)
    balance: Decimal
    currency: str
    payments: list[Payment] = Field(default_factory=list)
    # 3.0
    self_cert: str | None = None  # CRS901/CRS902
    dd_procedure: str | None = None  # CRS1201/CRS1202
    account_type: str | None = None  # CRS1101-1104
    joint_account_number: int | None = None
    equity_interest_types: list[str] = Field(default_factory=list)


class ReportingFI(Strict):
    estv_id: str  # SendingCompanyIN, e.g. 052.0000.0000
    uid: str | None = None  # IN, e.g. CHE-123.456.789; empty when the FI has no UID (70015)
    name: str  # official name; for a trustee-documented trust the trust's name, without "TDT="
    trustee_documented_trust: bool = False  # builder writes "TDT=" + name (Wegleitung 5.3.4)
    address: Address


class Message(Strict):
    reporting_fi: ReportingFI
    reporting_year: int
    accounts: list[Account] = Field(default_factory=list)
    message_type_indic: str = "CRS701"  # CRS703 for a nil report (no accounts)
    message_ref_id: str | None = None  # generated when empty


# --- checks --------------------------------------------------------------------------------


@dataclass(frozen=True)
class Problem:
    where: str  # e.g. "Accounts[key=A1].self_cert" or "ReportingFI.uid"
    message: str
    rule: str = ""  # ESTV error code or "XSD" / "3.0"


@dataclass
class Report:
    problems: list[Problem] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems

    def add(self, where: str, message: str, rule: str = "") -> None:
        self.problems.append(Problem(where, message, rule))


def _check_code(rep: Report, where: str, value: str | None, table: dict, *, required: bool,
                rule: str = "", allow_transitional: bool = False) -> None:  # fmt: skip
    if value is None or value == "":
        if required:
            rep.add(where, f"missing; one of {', '.join(table)}", rule)
        return
    if value in table:
        return
    if allow_transitional and value in codes.TRANSITIONAL:
        return
    rep.add(where, f"{value!r} is not one of {', '.join(table)}", rule)


def _check_country(rep: Report, where: str, value: str | None, *, required: bool) -> None:
    if not value:
        if required:
            rep.add(where, "missing ISO 3166-1 alpha-2 country code", "XSD")
        return
    if not COUNTRY_RE.match(value):
        rep.add(where, f"{value!r} is not a two-letter ISO country code", "XSD")


def _check_text(rep: Report, where: str, value: str | None) -> None:
    """Anhang 7.2 character set on a data element; the portal rejects the whole file (50005)."""
    if not value:
        return
    problems = ids.invalid_characters(value)
    if problems:
        first = problems[0]
        rep.add(where, f"{first.text!r} at position {first.position}: {first.reason}", "50005")


def _check_address(rep: Report, where: str, a: Address) -> None:
    _check_country(rep, f"{where}.country", a.country, required=True)
    for name in (
        "city",
        "street",
        "building_identifier",
        "suite_identifier",
        "floor_identifier",
        "district_name",
        "pob",
        "post_code",
        "country_subentity",
        "address_free",
    ):
        _check_text(rep, f"{where}.{name}", getattr(a, name))  # fmt: skip
    if not a.city:
        rep.add(f"{where}.city", "City is mandatory (AddressFix must be used)", "98104")
    if a.address_free is not None and not a.address_free:
        rep.add(f"{where}.address_free", "AddressFree, when present, must not be empty", "98104")
    _check_code(rep, f"{where}.legal_address_type", a.legal_address_type, codes.LEGAL_ADDRESS_TYPE,
                required=False)  # fmt: skip


def _check_person(rep: Report, where: str, p: Person, *, today: dt.date) -> None:
    if not p.first_name:
        rep.add(f"{where}.first_name", "FirstName is mandatory; use NFN if unknown", "50007")
    if not p.last_name:
        rep.add(f"{where}.last_name", "LastName is mandatory", "50007")
    for name in ("first_name", "last_name", "middle_name", "birth_city"):
        _check_text(rep, f"{where}.{name}", getattr(p, name))
    if p.name_type == "OECD201":
        rep.add(f"{where}.name_type", "nameType OECD201 is not allowed", "60004")
    else:
        _check_code(rep, f"{where}.name_type", p.name_type, codes.NAME_TYPE, required=False)
    if not p.residence_countries:
        rep.add(f"{where}.residence_countries", "at least one ResCountryCode is mandatory", "XSD")
    for i, c in enumerate(p.residence_countries):
        _check_country(rep, f"{where}.residence_countries[{i}]", c, required=True)
    for i, t in enumerate(p.tins):
        if not t.value:
            rep.add(f"{where}.tins[{i}]", "a TIN, when present, must not be empty", "XSD")
        _check_text(rep, f"{where}.tins[{i}]", t.value)
        _check_country(rep, f"{where}.tins[{i}].issued_by", t.issued_by, required=False)
    if p.birth_date is not None and not (dt.date(1900, 1, 1) < p.birth_date < today):
        rep.add(f"{where}.birth_date", "must be after 1900-01-01 and before today", "60014")
    _check_country(rep, f"{where}.birth_country", p.birth_country, required=False)
    _check_address(rep, f"{where}.address", p.address)


def _check_organisation(rep: Report, where: str, o: Organisation) -> None:
    if not o.name:
        rep.add(f"{where}.name", "organisation Name is mandatory", "XSD")
    _check_text(rep, f"{where}.name", o.name)
    if o.name_type == "OECD201":
        rep.add(f"{where}.name_type", "nameType OECD201 is not allowed", "60004")
    _check_code(rep, f"{where}.acct_holder_type", o.acct_holder_type, codes.ACCT_HOLDER_TYPE,
                required=True, rule="XSD")  # fmt: skip
    if not o.residence_countries:
        rep.add(f"{where}.residence_countries", "at least one ResCountryCode is mandatory", "XSD")
    for i, c in enumerate(o.residence_countries):
        _check_country(rep, f"{where}.residence_countries[{i}]", c, required=True)
    for i, t in enumerate(o.ins):
        if not t.value:
            rep.add(f"{where}.ins[{i}]", "an IN, when present, must not be empty", "XSD")
        _check_text(rep, f"{where}.ins[{i}]", t.value)
    _check_address(rep, f"{where}.address", o.address)


def check_account(rep: Report, acc: Account, version: Version, *, today: dt.date) -> None:
    w = f"Accounts[key={acc.key}]"
    if not acc.account_number:
        rep.add(f"{w}.account_number", "mandatory; use NANUM when there is no number", "50007")
    _check_text(rep, f"{w}.account_number", acc.account_number)
    _check_text(rep, f"{w}.doc_ref_id", acc.doc_ref_id)
    _check_code(rep, f"{w}.account_number_type", acc.account_number_type, codes.ACCT_NUMBER_TYPE,
                required=False)  # fmt: skip
    if acc.balance < 0:
        rep.add(f"{w}.balance", "AccountBalance must not be negative", "60002")
    if acc.closed and acc.balance != 0:
        rep.add(f"{w}.balance", "closed accounts must report a balance of 0", "60003")
    if not CURRENCY_RE.match(acc.currency or ""):
        rep.add(f"{w}.currency", "ISO 4217 currency code required", "XSD")

    # holder
    if (acc.holder_person is None) == (acc.holder_organisation is None):
        rep.add(f"{w}.holder", "exactly one of individual / organisation holder is required", "XSD")
    if acc.holder_person is not None:
        _check_person(rep, f"{w}.holder", acc.holder_person, today=today)
        if acc.controlling_persons:
            rep.add(f"{w}.controlling_persons",
                    "no ControllingPerson allowed for an individual holder", "60005")  # fmt: skip
        if acc.undocumented and acc.holder_person.residence_countries != ["CH"]:
            rep.add(f"{w}.holder.residence_countries",
                    "undocumented account: the only ResCountryCode must be CH", "98203")  # fmt: skip
    if acc.holder_organisation is not None:
        _check_organisation(rep, f"{w}.holder", acc.holder_organisation)
        aht = acc.holder_organisation.acct_holder_type
        if aht == "CRS101" and not acc.controlling_persons:
            rep.add(f"{w}.controlling_persons",
                    "CRS101 holder: at least one ControllingPerson is required", "60006")  # fmt: skip
        if aht in ("CRS102", "CRS103") and acc.controlling_persons:
            rep.add(f"{w}.controlling_persons",
                    f"no ControllingPerson allowed for AcctHolderType {aht}", "60005")  # fmt: skip
        if acc.undocumented:
            rep.add(f"{w}.undocumented",
                    "undocumented accounts must have an individual holder", "98203")  # fmt: skip

    for i, cp in enumerate(acc.controlling_persons):
        cw = f"{w}.controlling_persons[{i}]"
        _check_person(rep, cw, cp.person, today=today)
        if version == "3.0":
            if not cp.ctrlg_person_types:
                rep.add(f"{cw}.ctrlg_person_types",
                        "3.0: at least one CtrlgPersonType is mandatory", "3.0")  # fmt: skip
            _check_code(rep, f"{cw}.self_cert", cp.self_cert, codes.SELF_CERT_CP, required=True,
                        rule="3.0", allow_transitional=True)  # fmt: skip
        elif len(cp.ctrlg_person_types) > 1:
            rep.add(f"{cw}.ctrlg_person_types",
                    "2.0 allows one CtrlgPersonType; only the first is written", "info")  # fmt: skip
        for j, t in enumerate(cp.ctrlg_person_types):
            _check_code(rep, f"{cw}.ctrlg_person_types[{j}]", t, codes.CTRLG_PERSON_TYPE,
                        required=True, allow_transitional=(version == "3.0"))  # fmt: skip

    for i, p in enumerate(acc.payments):
        pw = f"{w}.payments[{i}]"
        _check_code(rep, f"{pw}.payment_type", p.payment_type, codes.PAYMENT_TYPE, required=True,
                    rule="XSD")  # fmt: skip
        if not CURRENCY_RE.match(p.currency or ""):
            rep.add(f"{pw}.currency", "ISO 4217 currency code required", "XSD")

    # 3.0-only elements
    if version == "3.0":
        _check_code(rep, f"{w}.self_cert", acc.self_cert, codes.SELF_CERT, required=True,
                    rule="3.0", allow_transitional=True)  # fmt: skip
        _check_code(rep, f"{w}.dd_procedure", acc.dd_procedure, codes.DD_PROCEDURE, required=True,
                    rule="3.0", allow_transitional=True)  # fmt: skip
        _check_code(rep, f"{w}.account_type", acc.account_type, codes.ACCOUNT_TYPE, required=True,
                    rule="3.0", allow_transitional=True)  # fmt: skip
        for j, e in enumerate(acc.equity_interest_types):
            _check_code(rep, f"{w}.equity_interest_types[{j}]", e, codes.EQUITY_INTEREST_TYPE,
                        required=True, rule="XSD")  # fmt: skip
        if acc.joint_account_number is not None and not 1 <= acc.joint_account_number <= 200:
            rep.add(f"{w}.joint_account_number", "JointAccount.Number must be 1-200", "XSD")
        # ESTV cross-field rules 60017-60023 (prose of 60018 wins over its formula)
        ant, at = acc.account_number_type, acc.account_type
        if ant in ("OECD606", "OECD601") and at not in (None, "CRS1101", "CRS1100"):
            rule = "60017" if ant == "OECD606" else "60018"
            rep.add(f"{w}.account_type", f"{ant} accounts must be depository (CRS1101)", rule)
        if acc.equity_interest_types and at not in (None, "CRS1104", "CRS1100"):
            rep.add(f"{w}.account_type",
                    "EquityInterestType given: AccountType must be CRS1104", "60019")  # fmt: skip
        if at == "CRS1103" and ant not in (None, "OECD605"):
            rep.add(f"{w}.account_number_type",
                    "CRS1103 accounts must use AcctNumberType OECD605", "60020")  # fmt: skip
        for i, p in enumerate(acc.payments):
            if at == "CRS1101" and p.payment_type != "CRS502":
                rep.add(f"{w}.payments[{i}].payment_type",
                        "depository account (CRS1101): only interest (CRS502)", "60021")  # fmt: skip
            if at in ("CRS1104", "CRS1103") and p.payment_type not in ("CRS503", "CRS504"):
                rule = "60022" if at == "CRS1104" else "60023"
                rep.add(f"{w}.payments[{i}].payment_type",
                        f"{at} accounts: only CRS503 or CRS504 payments", rule)  # fmt: skip
    else:
        for name in ("self_cert", "dd_procedure", "account_type"):
            if getattr(acc, name):
                rep.add(f"{w}.{name}", "ignored in 2.0 (element does not exist)", "info")


def check_message(msg: Message, version: Version, *, today: dt.date | None = None) -> Report:
    """All problems of a message for the given schema version; empty report means buildable."""
    today = today or dt.datetime.now(tz=dt.UTC).date()
    rep = Report()
    fi = msg.reporting_fi
    if not fi.estv_id:
        rep.add("ReportingFI.estv_id", "SendingCompanyIN must be the ESTV-ID of the FI", "98001")
    elif not ESTV_ID_RE.match(fi.estv_id):
        rep.add("ReportingFI.estv_id",
                "does not look like the ESTV-ID example (052.0000.0000); the portal compares it "
                "with the registered value", "info")  # fmt: skip
    _check_text(rep, "ReportingFI.estv_id", fi.estv_id)
    if fi.uid and not UID_RE.match(fi.uid):
        rep.add("ReportingFI.uid", "IN, when given, must be the UID (CHE-nnn.nnn.nnn)", "70015")
    if not fi.name:
        rep.add("ReportingFI.name", "Name is mandatory", "XSD")
    elif fi.name.upper().startswith(TDT_PREFIX) and not fi.trustee_documented_trust:
        rep.add("ReportingFI.name",
                "starts with TDT= but trustee_documented_trust is not set: write the trust's name "
                "and set the flag, the prefix is added at build time", "5.3.4")  # fmt: skip
    _check_text(rep, "ReportingFI.name", fi.name)
    _check_address(rep, "ReportingFI.address", fi.address)
    if not 2017 <= msg.reporting_year <= today.year:
        rep.add("ReportingFI.reporting_year", "reporting year must be 2017..current year", "98003")
    _check_code(rep, "Message.message_type_indic", msg.message_type_indic, codes.MESSAGE_TYPE_INDIC,
                required=True, rule="98004")  # fmt: skip
    if msg.message_type_indic == "CRS702":
        rep.add("Message.message_type_indic",
                "CRS702 (corrections) is not supported yet: a correction needs the DocRefIds of the "
                "records sent before (submission registry, Wegleitung Ziffer 6)", "80010")  # fmt: skip
    if msg.message_type_indic == "CRS703" and msg.accounts:
        rep.add("Message.accounts", "a nil report (CRS703) must not contain accounts", "98005")
    if msg.message_type_indic != "CRS703" and not msg.accounts:
        rep.add("Message.accounts", "at least one account is required unless CRS703", "60015")
    keys = [a.key for a in msg.accounts]
    for k in sorted({k for k in keys if keys.count(k) > 1}):
        rep.add(f"Accounts[key={k}]", "account key is not unique", "input")
    refs = [a.doc_ref_id for a in msg.accounts if a.doc_ref_id]
    for r in sorted({r for r in refs if refs.count(r) > 1}):
        rep.add(f"Accounts[doc_ref_id={r}]", "DocRefId used on more than one row", "80000")
    for acc in msg.accounts:
        check_account(rep, acc, version, today=today)
    _check_joint_accounts(rep, msg, version)
    return rep


def _check_joint_accounts(rep: Report, msg: Message, version: Version) -> None:
    """Joint accounts: one AccountReport per reportable holder with the same account number and
    the full balance; in 3.0 every row carries JointAccount.Number = number of joint holders."""
    if version != "3.0":
        return
    by_number: dict[str, list[Account]] = {}
    for acc in msg.accounts:
        if acc.account_number and acc.account_number != codes.NO_ACCOUNT_NUMBER:
            by_number.setdefault(acc.account_number, []).append(acc)
    for number, rows in by_number.items():
        if len(rows) < 2:
            continue
        numbers = {a.joint_account_number for a in rows}
        if None in numbers or len(numbers) > 1:
            rep.add(f"Accounts[account_number={number}]",
                    f"{len(rows)} rows share this account number: for a joint account set "
                    "joint_account_number (number of joint holders) to the same value on every "
                    "row; otherwise use distinct account numbers", "3.0")  # fmt: skip
