# Flat input format (contract)

Generated from `src/aeoi/crs/flat.py` by `python tools/render_flat_format.py` — edit the code, not
this file. The Excel template (`aeoi crs template --out template.xlsx`) is generated from the same
definitions; `--example` fills it with invented data.

One workbook (or one folder of `<Sheet>.csv` files, `;`-separated, UTF-8) = one reporting FI = one
CRS message. Sheets: `ReportingFI` (field/value rows), `Accounts` (one row per account, holder
inline), `ControllingPersons` and `Payments` (linked to the account by `key`).

Conventions: several values in one cell are separated by `;`; TINs/INs are `value@CC`
(issuing country optional); booleans accept true/false, 1/0, yes/no, ja/nein, oui/non; dates are
`YYYY-MM-DD`, `DD.MM.YYYY` or Excel dates; amounts are numbers with a dot (or Excel numbers).
Codes are the OECD values (see `src/aeoi/crs/codes.py` and the `Codes` sheet). Columns marked
"3.0" are mandatory for CRS schema 3.0 and ignored for 2.0. Empty `doc_ref_id` cells are filled
with generated `CH<year>CH<uuid>` identifiers at build time; a DocRefId can never be reused
(ESTV 80000), so fill the column only with identifiers that have never been sent.

Joint accounts: one row per reportable holder, same `account_number`, the full balance on each
row, and for 3.0 `joint_account_number` = number of joint holders on every row. Trustee-documented
trusts: the trust's name in `ReportingFI.name` plus `trustee_documented_trust = true`; the builder
writes `TDT=` before the name (ESTV 5.3.4). `uid` may be empty when the FI has no UID (70015).
Corrections (`CRS702`) are refused until the submission registry exists.


## ReportingFI

| column | required | kind | description |
|---|---|---|---|
| `estv_id` | yes | text | ESTV-ID of the reporting FI (SendingCompanyIN), e.g. 052.0000.0000 |
| `uid` |  | text | UID of the reporting FI (IN), e.g. CHE-123.456.789; leave empty if the FI has no UID |
| `name` | yes | text | Official name of the reporting FI; for a trustee-documented trust the trust's name (without TDT=) |
| `trustee_documented_trust` |  | bool | true if this is a Trustee-Documented Trust: 'TDT=' is put before the name (ESTV 5.3.4) |
| `reporting_year` | yes | int | Reporting year (calendar year the data refers to) |
| `message_type_indic` |  | text | CRS701 new data / CRS703 nil report (no accounts) Codes: CRS701, CRS702, CRS703. |
| `address_country` | yes | text | Country of the address, ISO 3166-1 alpha-2 (e.g. CH) |
| `address_street` |  | text | Street (AddressFix.Street) |
| `address_building` |  | text | Building identifier / house number |
| `address_suite` |  | text | Suite identifier |
| `address_floor` |  | text | Floor identifier |
| `address_district` |  | text | District name |
| `address_pob` |  | text | P.O. box |
| `address_post_code` |  | text | Postal code |
| `address_city` | yes | text | City - mandatory, AddressFix must be used (ESTV 98104) |
| `address_subentity` |  | text | Country subentity (canton, state) |
| `address_free` |  | text | Optional free-text address in addition to the fixed parts |
| `legal_address_type` |  | text | OECD301-305 Codes: OECD301, OECD302, OECD303, OECD304, OECD305. |

## Accounts

| column | required | kind | description |
|---|---|---|---|
| `key` | yes | text | Row identifier, unique per workbook; links ControllingPersons and Payments |
| `doc_ref_id` |  | text | Leave empty: generated (CH<year>CH<uuid>). Fill only to fix an identifier that has never been sent (a DocRefId can never be reused, ESTV 80000) |
| `account_number` | yes | text | Account number; NANUM if none (ESTV 5.3.7) |
| `account_number_type` |  | text | OECD601 IBAN, 602 OBAN, 603 ISIN, 604 OSIN, 605 Other, 606 e-money Codes: OECD601, OECD602, OECD603, OECD604, OECD605, OECD606. |
| `undocumented` |  | bool | true/false - undocumented account (holder must be CH individual) |
| `closed` |  | bool | true/false - closed during the year (balance must be 0) |
| `dormant` |  | bool | true/false - dormant account |
| `holder_type` | yes | text | individual or organisation Codes: individual, organisation. |
| `first_name` | if individual | text | First name; NFN if none (ESTV 5.3.8) |
| `last_name` | if individual | text | Last name |
| `middle_name` |  | text | Middle name |
| `name_type` |  | text | OECD202-208 (OECD201 not allowed) Codes: OECD202, OECD203, OECD204, OECD205, OECD206, OECD207, OECD208. |
| `birth_date` |  | date | Date of birth YYYY-MM-DD (after 1900-01-01) |
| `birth_city` |  | text | City of birth |
| `birth_country` |  | text | Country of birth, ISO alpha-2 |
| `residence_countries` | yes | multi | Tax residence countries, ISO alpha-2, ';'-separated |
| `tins` |  | tins | TINs as value@CC;value@CC (CC = issuing country, optional) |
| `nationalities` |  | multi | Nationalities, ISO alpha-2, ';'-separated |
| `org_name` | if organisation | text | Organisation: legal name |
| `org_name_type` |  | text | Organisation: OECD202-208 Codes: OECD202, OECD203, OECD204, OECD205, OECD206, OECD207, OECD208. |
| `acct_holder_type` | if organisation | text | Organisation: CRS101 passive NFE with CPs / CRS102 reportable person / CRS103 passive NFE reportable Codes: CRS101, CRS102, CRS103. |
| `org_ins` |  | tins | Organisation: INs as value@CC;value@CC |
| `address_country` | yes | text | Country of the address, ISO 3166-1 alpha-2 (e.g. CH) |
| `address_street` |  | text | Street (AddressFix.Street) |
| `address_building` |  | text | Building identifier / house number |
| `address_suite` |  | text | Suite identifier |
| `address_floor` |  | text | Floor identifier |
| `address_district` |  | text | District name |
| `address_pob` |  | text | P.O. box |
| `address_post_code` |  | text | Postal code |
| `address_city` | yes | text | City - mandatory, AddressFix must be used (ESTV 98104) |
| `address_subentity` |  | text | Country subentity (canton, state) |
| `address_free` |  | text | Optional free-text address in addition to the fixed parts |
| `legal_address_type` |  | text | OECD301-305 Codes: OECD301, OECD302, OECD303, OECD304, OECD305. |
| `balance` | yes | decimal | Account balance at year end, >= 0 (0 if closed) |
| `currency` | yes | text | ISO 4217 currency of the balance (CHF, EUR, USD ...) |
| `self_cert` |  | text | 3.0: CRS901 valid self-certification / CRS902 none Codes: CRS901, CRS902. |
| `dd_procedure` |  | text | 3.0: CRS1201 new account / CRS1202 preexisting account Codes: CRS1201, CRS1202. |
| `account_type` |  | text | 3.0: CRS1101 depository / 1102 custodial / 1103 insurance-annuity / 1104 equity-debt interest Codes: CRS1101, CRS1102, CRS1103, CRS1104. |
| `joint_account_number` |  | int | 3.0: number of joint holders (1-200), optional |
| `equity_interest_types` |  | multi | 3.0: CRS401-410, ';'-separated, only with account_type CRS1104 Codes: CRS401, CRS402, CRS403, CRS404, CRS405, CRS406, CRS407, CRS408, CRS409, CRS410. |

## ControllingPersons

| column | required | kind | description |
|---|---|---|---|
| `key` | yes | text | Key of the account (Accounts.key) |
| `first_name` | yes | text | First name; NFN if none (ESTV 5.3.8) |
| `last_name` | yes | text | Last name |
| `middle_name` |  | text | Middle name |
| `name_type` |  | text | OECD202-208 (OECD201 not allowed) Codes: OECD202, OECD203, OECD204, OECD205, OECD206, OECD207, OECD208. |
| `birth_date` |  | date | Date of birth YYYY-MM-DD (after 1900-01-01) |
| `birth_city` |  | text | City of birth |
| `birth_country` |  | text | Country of birth, ISO alpha-2 |
| `residence_countries` | yes | multi | Tax residence countries, ISO alpha-2, ';'-separated |
| `tins` |  | tins | TINs as value@CC;value@CC (CC = issuing country, optional) |
| `nationalities` |  | multi | Nationalities, ISO alpha-2, ';'-separated |
| `address_country` | yes | text | Country of the address, ISO 3166-1 alpha-2 (e.g. CH) |
| `address_street` |  | text | Street (AddressFix.Street) |
| `address_building` |  | text | Building identifier / house number |
| `address_suite` |  | text | Suite identifier |
| `address_floor` |  | text | Floor identifier |
| `address_district` |  | text | District name |
| `address_pob` |  | text | P.O. box |
| `address_post_code` |  | text | Postal code |
| `address_city` | yes | text | City - mandatory, AddressFix must be used (ESTV 98104) |
| `address_subentity` |  | text | Country subentity (canton, state) |
| `address_free` |  | text | Optional free-text address in addition to the fixed parts |
| `legal_address_type` |  | text | OECD301-305 Codes: OECD301, OECD302, OECD303, OECD304, OECD305. |
| `ctrlg_person_types` |  | multi | CRS801-813, ';'-separated (3.0: at least one) Codes: CRS801, CRS802, CRS803, CRS804, CRS805, CRS806, CRS807, CRS808, CRS809, CRS810, CRS811, CRS812, CRS813. |
| `self_cert` |  | text | 3.0: CRS1001 valid self-certification / CRS1002 none Codes: CRS1001, CRS1002. |

## Payments

| column | required | kind | description |
|---|---|---|---|
| `key` | yes | text | Key of the account (Accounts.key) |
| `payment_type` | yes | text | CRS501 dividends / 502 interest / 503 gross proceeds / 504 other Codes: CRS501, CRS502, CRS503, CRS504. |
| `amount` | yes | decimal | Amount, >= 0 |
| `currency` | yes | text | ISO 4217 currency |
