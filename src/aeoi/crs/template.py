"""Excel template for the flat input format, generated from :mod:`aeoi.crs.flat`.

The template has the four data sheets with header comments and drop-down validations for every
coded column, a ``Codes`` sheet with every allowed value and its meaning, and a ``ReadMe`` sheet.
``write_message`` fills a workbook from a :class:`Message` (used for the example and for tests).
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from aeoi.crs import codes
from aeoi.crs.flat import SHEETS, Column
from aeoi.crs.model import Account, Address, Message, Person, Tin

HEADER_FILL = PatternFill("solid", fgColor="DDEBF7")
REQUIRED_FILL = PatternFill("solid", fgColor="FFF2CC")
CONDITIONAL_FILL = PatternFill("solid", fgColor="FCE4D6")


def _fill(required: bool | str) -> PatternFill:
    if required is True:
        return REQUIRED_FILL
    if required:
        return CONDITIONAL_FILL
    return HEADER_FILL


MAX_ROWS = 5000

README = """aeoi - CRS reporting template

One workbook = one reporting financial institution = one CRS message to the ESTV.

Sheets
- ReportingFI: one value per row (field / value).
- Accounts: one row per reportable account; the holder's data is on the same row.
  holder_type decides which columns count: 'individual' uses first_name ... nationalities,
  'organisation' uses org_name, org_name_type, acct_holder_type, org_ins.
- ControllingPersons: one row per controlling person of an organisation holder with
  acct_holder_type CRS101; 'key' is the account's key.
- Payments: one row per payment of the year; 'key' is the account's key.

Conventions
- Several values in one cell: separate with ';' (e.g. CH;DE).
- TINs / INs: value@CC (CC = issuing country), several separated by ';'.
- true/false columns accept true/false, 1/0, yes/no, ja/nein, oui/non.
- Dates: YYYY-MM-DD or an Excel date. Amounts: numbers, dot as decimal separator.
- Yellow headers are mandatory; orange headers are mandatory for one holder_type only
  (first_name/last_name for 'individual', org_name/acct_holder_type for 'organisation').
  Columns marked 3.0 are mandatory for CRS schema 3.0 (ESTV: only 3.0 from 16.01.2027),
  ignored for 2.0.
- Joint accounts: one row per reportable holder, same account_number, the FULL balance on
  each row; for 3.0 put the number of joint holders in joint_account_number on every row.
- Trustee-documented trusts: put the trust's name in ReportingFI.name and set
  trustee_documented_trust = true; the 'TDT=' prefix required by the ESTV is added at build time.
- Corrections (CRS702) are not supported yet: a correction needs the identifiers of the records
  already sent, which the submission registry will provide.
- Allowed characters: ISO 8859-1 without ! " # $ < > ^ ~ and the symbols listed by the ESTV
  (Anhang 7.2); never the sequences --  /*  &#

Every code used in a drop-down is explained on the 'Codes' sheet.
"""


def _add_validation(ws, col_idx: int, values: list[str]) -> None:
    formula = '"' + ",".join(values) + '"'
    if len(formula) > 255:  # Excel limit for inline lists: fall back to no validation
        return
    dv = DataValidation(type="list", formula1=formula, allow_blank=True, showErrorMessage=True)
    dv.error = "Choose one of the listed codes (see sheet Codes)"
    ws.add_data_validation(dv)
    letter = get_column_letter(col_idx)
    dv.add(f"{letter}2:{letter}{MAX_ROWS}")


def _write_table(ws, columns: list[Column]) -> None:
    for i, col in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=i, value=col.name)
        cell.font = Font(bold=True)
        cell.fill = _fill(col.required)
        note = col.description
        if isinstance(col.required, str):
            note += f" - mandatory when holder_type = {col.required}"
        cell.comment = Comment(note, "aeoi")
        ws.column_dimensions[get_column_letter(i)].width = max(14, min(32, len(col.name) + 4))
        if col.codes and col.kind != "multi":
            _add_validation(ws, i, list(col.codes))
        if col.kind == "bool":
            _add_validation(ws, i, ["true", "false"])
    ws.freeze_panes = "A2"


def _write_reporting_fi(ws, columns: list[Column]) -> None:
    ws["A1"], ws["B1"], ws["C1"] = "field", "value", "description"
    for c in ("A1", "B1", "C1"):
        ws[c].font = Font(bold=True)
        ws[c].fill = HEADER_FILL
    for i, col in enumerate(columns, start=2):
        ws.cell(row=i, column=1, value=col.name).fill = (
            REQUIRED_FILL if col.required else HEADER_FILL
        )
        ws.cell(row=i, column=3, value=col.description)
        if col.codes:
            dv = DataValidation(
                type="list", formula1='"' + ",".join(col.codes) + '"', allow_blank=True
            )
            ws.add_data_validation(dv)
            dv.add(f"B{i}")
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 34
    ws.column_dimensions["C"].width = 80


def _write_codes(ws) -> None:
    ws.append(["code list", "code", "meaning"])
    for c in ws[1]:
        c.font = Font(bold=True)
    tables = {
        "acct_holder_type": codes.ACCT_HOLDER_TYPE,
        "equity_interest_types (3.0)": codes.EQUITY_INTEREST_TYPE,
        "payment_type": codes.PAYMENT_TYPE,
        "message_type_indic": codes.MESSAGE_TYPE_INDIC,
        "ctrlg_person_types": codes.CTRLG_PERSON_TYPE,
        "self_cert - account holder (3.0)": codes.SELF_CERT,
        "self_cert - controlling person (3.0)": codes.SELF_CERT_CP,
        "account_type (3.0)": codes.ACCOUNT_TYPE,
        "dd_procedure (3.0)": codes.DD_PROCEDURE,
        "transitional values (3.0, records first sent under 2.0 - ESTV acceptance open)": codes.TRANSITIONAL,
        "name_type": codes.NAME_TYPE,
        "legal_address_type": codes.LEGAL_ADDRESS_TYPE,
        "account_number_type": codes.ACCT_NUMBER_TYPE,
    }
    for title, table in tables.items():
        for code, meaning in table.items():
            ws.append([title, code, meaning])
    ws.column_dimensions["A"].width = 44
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 100
    ws.freeze_panes = "A2"


def new_workbook() -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = "ReadMe"
    ws["A1"] = README
    ws["A1"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 110
    ws.row_dimensions[1].height = 400
    for name, columns in SHEETS.items():
        sheet = wb.create_sheet(name)
        if name == "ReportingFI":
            _write_reporting_fi(sheet, columns)
        else:
            _write_table(sheet, columns)
    _write_codes(wb.create_sheet("Codes"))
    return wb


# --- filling a workbook from a message (example file, tests) ---------------------------------


def _address_cells(a: Address) -> dict[str, object]:
    return {
        "address_country": a.country,
        "address_street": a.street,
        "address_building": a.building_identifier,
        "address_suite": a.suite_identifier,
        "address_floor": a.floor_identifier,
        "address_district": a.district_name,
        "address_pob": a.pob,
        "address_post_code": a.post_code,
        "address_city": a.city,
        "address_subentity": a.country_subentity,
        "address_free": a.address_free,
        "legal_address_type": a.legal_address_type,
    }


def _tins_cell(tins: list[Tin]) -> str:
    return ";".join(t.value + (f"@{t.issued_by}" if t.issued_by else "") for t in tins)


def _person_cells(p: Person) -> dict[str, object]:
    return {
        "first_name": p.first_name,
        "last_name": p.last_name,
        "middle_name": p.middle_name,
        "name_type": p.name_type,
        "birth_date": p.birth_date,
        "birth_city": p.birth_city,
        "birth_country": p.birth_country,
        "residence_countries": ";".join(p.residence_countries),
        "tins": _tins_cell(p.tins),
        "nationalities": ";".join(p.nationalities),
        **_address_cells(p.address),
    }


def _account_cells(a: Account) -> dict[str, object]:
    cells: dict[str, object] = {
        "key": a.key,
        "doc_ref_id": a.doc_ref_id,
        "account_number": a.account_number,
        "account_number_type": a.account_number_type,
        "undocumented": "true" if a.undocumented else "false",
        "closed": "true" if a.closed else "false",
        "dormant": "true" if a.dormant else "false",
        "balance": a.balance,
        "currency": a.currency,
        "self_cert": a.self_cert,
        "dd_procedure": a.dd_procedure,
        "account_type": a.account_type,
        "joint_account_number": a.joint_account_number,
        "equity_interest_types": ";".join(a.equity_interest_types),
    }
    if a.holder_person is not None:
        cells["holder_type"] = "individual"
        cells.update(_person_cells(a.holder_person))
    else:
        o = a.holder_organisation
        assert o is not None
        cells["holder_type"] = "organisation"
        cells.update(
            {
                "org_name": o.name,
                "org_name_type": o.name_type,
                "acct_holder_type": o.acct_holder_type,
                "org_ins": _tins_cell(o.ins),
                "residence_countries": ";".join(o.residence_countries),
                **_address_cells(o.address),
            }
        )
    return cells


def _append(ws, columns: list[Column], cells: dict[str, object]) -> None:
    row = []
    for col in columns:
        v = cells.get(col.name)
        if isinstance(v, dt.date):
            row.append(v)
        elif v is None or v == "":
            row.append(None)
        else:
            row.append(v)
    ws.append(row)


def write_message(msg: Message, path: str | Path) -> None:
    """Write a message into a fresh template workbook (example data, round-trip tests)."""
    wb = new_workbook()
    fi = msg.reporting_fi
    values = {
        "estv_id": fi.estv_id,
        "uid": fi.uid,
        "name": fi.name,
        "trustee_documented_trust": "true" if fi.trustee_documented_trust else "false",
        "reporting_year": msg.reporting_year,
        "message_type_indic": msg.message_type_indic,
        **_address_cells(fi.address),
    }
    ws = wb["ReportingFI"]
    for row in ws.iter_rows(min_row=2, max_col=1):
        cell = row[0]
        if cell.value in values and values[cell.value] not in (None, ""):
            ws.cell(row=cell.row, column=2, value=values[cell.value])
    for acc in msg.accounts:
        _append(wb["Accounts"], SHEETS["Accounts"], _account_cells(acc))
        for cp in acc.controlling_persons:
            _append(
                wb["ControllingPersons"],
                SHEETS["ControllingPersons"],
                {
                    "key": acc.key,
                    **_person_cells(cp.person),
                    "ctrlg_person_types": ";".join(cp.ctrlg_person_types),
                    "self_cert": cp.self_cert,
                },
            )
        for p in acc.payments:
            _append(
                wb["Payments"],
                SHEETS["Payments"],
                {
                    "key": acc.key,
                    "payment_type": p.payment_type,
                    "amount": p.amount,
                    "currency": p.currency,
                },
            )
    wb.save(path)


def write_template(path: str | Path) -> None:
    new_workbook().save(path)
