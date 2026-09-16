# Handoff — state of the project (updated 2026-09-16)

Read this first in any new session. It is the memory of the project when the chat history is not
at hand.

## What we are building

`aeoi`: open toolkit that turns a flat table of reportable accounts into the XML files tax
administrations require for the automatic exchange of information — CRS (OECD XML Schema 3.0,
mandatory at the Swiss ESTV from 16.01.2027; 2.0 accepted until 14.12.2026), later CARF and FATCA.
Validates against the XSD, the OECD business rules and the portal rules, packages/encrypts for
upload, keeps a local registry of what was sent, builds corrections, parses the returned status.

Why: no open implementation exists (GitHub/PyPI: zero); the closed ones are priced per named user
(TRSuite: 1'169 USD for 1-3 users, +40 %/year maintenance; others on request). Swiss market:
~9'000 reporting FIs registered at the ESTV, mostly vehicles run by fiduciaries.

## Decisions taken

- Python first (xsdata models, lxml/xmlschema, pydantic domain), Rust only later for a WASM
  browser validator. Apache-2.0 core + DCO; PRO packs proprietary.
- Module order: CRS 3.0 for Switzerland → CARF 1.5 (Jan–Feb 2027) → portal packs BZSt, HMRC, ACD
  (verify each portal's envelope before promising) → FATCA/IDES last.
- Price per organisation, reporting FIs unlimited, bands by number of vehicles: 1-10: 900 CHF/yr,
  11-50: 1'500, more: 2'400, support included; library licence for software houses 2'500 CHF/yr.
- The pilot reporting FI is a prerequisite (portal access, `ESTV-PublicKey.pem`, test uploads).
  The pilot sends validation results (DocRefId + codes), never the file.
- Gates: mid-Dec 2026 developer signals in OR (pypistats without mirrors, issues from strangers,
  files validated in the browser, requests via associations); mid-Mar 2027 three pilots with real
  files validated on the ESTV test channel; 31 May 2027 three paid licences or one library
  licence; hard close 30 June 2027.
- Week-6 pilot test uses a **2.0** payload (transport pipeline only); first **3.0** test in the week
  of 16.01.2027.

## What exists (see README.md)

- Pinned sources with SHA-256: `docs/SOURCES.md` from `docs/sources/manifest.json`; OECD files
  committed (CC BY 4.0), ESTV PDFs not committed — `python tools/pin_sources.py --fetch`.
- Generated models: `src/aeoi/schemas/` (`tools/generate_models.py`, includes the Address_Type
  field-order patch).
- ESTV packaging/encryption: `src/aeoi/estv/packaging.py`; identifiers and charset:
  `src/aeoi/estv/ids.py`; CLI `aeoi estv package|inspect`.
- Corpus: `tests/corpus/estv_v2/` (five Wegleitung annex examples, valid, round-trip valid).
- Week 2 (done): flat input format `docs/FLAT-FORMAT.md` (`aeoi.crs.flat`, template in
  `aeoi.crs.template`), domain model with version-aware talking checks (`aeoi.crs.model`),
  builder to 2.0/3.0 XML (`aeoi.crs.build`), example message (`aeoi.crs.example`), CLI
  `aeoi crs template|check|build`. End-to-end: workbook -> check -> XML (valid 2.0 and 3.0) ->
  ESTV package.
- 113 tests: `.venv/Scripts/python -m pytest`.

## Verified facts to keep

- Wegleitung 3.3.1: CRS_Payload.xml → zip → AES-256-CBC (fresh IV, PKCS#7) → key+IV 48 bytes in
  RSA PKCS#1 v1.5 → zip {CRS_Payload, CRS_KEY}; test files start with "Test"; XML ≤ 100 MB,
  package ≤ 10 MB; XML must not be signed (50007).
- 67 distinct ESTV error codes; ESTV-specific range 98000-98999; ReportingFI cannot be corrected or
  cancelled (80004); CorrMessageRefId forbidden (80006); DocRefId = CH+year+CH+1-42 chars
  (80001); MessageRefId `CH[0-9]{4}CH.{1,162}`, UUID recommended, no customer data (50008/50009);
  ISO 8859-1 minus Anhang 7.2 (50005); test DocTypeIndic OECD10/OECD11.
- XSD 3.0 vs 2.0 (verified on `CrsXML_v3.0.xsd`, tests by construction in
  `tests/test_models_roundtrip.py`):
  - new **mandatory**: `SelfCert` in AccountHolder and in ControllingPerson; `DDProcedure` and
    `AccountType` in AccountReport; `CtrlgPersonType` goes from optional (2.0) to mandatory and
    repeatable (3.0);
  - **optional**: `JointAccount` (AccountReport), `EquityInterestType` (AccountHolder, 0..n);
  - **element order** (the week-2 mapping must respect it): AccountHolder = `EquityInterestType*`,
    `SelfCert`, then `Individual` | (`Organisation`, `AcctHolderType`); ControllingPerson =
    `Individual`, `CtrlgPersonType+`, `SelfCert` (last); AccountReport = DocSpec, AccountNumber,
    AccountHolder, ControllingPerson*, AccountBalance, Payment*, `DDProcedure`, `AccountType`,
    `JointAccount?`;
  - transitional "not reported" values exist in 3.0 for records first sent under 2.0: CRS800
    (CtrlgPersonType), CRS900 (SelfCert holder), CRS1000 (SelfCert controlling person), CRS1100
    (AccountType), CRS1200 (DDProcedure). The Wegleitung does not mention them — pilot question.
  - the 3.0 generator emits only `urn:oecd:ties:crs:v3`; the validator accepts v2 and v3 and
    reports the mismatch with the Wegleitung example.
- Open discrepancies: `docs/OPEN-QUESTIONS.md` (namespace v2 vs v3 in the 3.0 header, the
  14.12–16.01 gap, transitional values, status message format, rule-text typos 60018/60021).
- Size limits are decimal (100'000'000 / 10'000'000 bytes): the stricter reading of "100 MB / 10 MB".
- Character set: Anhang 7.2 exclusions plus control characters (C0 except tab/LF/CR, DEL, C1);
  the serializer writes raw UTF-8, never numeric references (`&#` is a forbidden sequence).

## Next steps

1. Week 2: done (see above). Open: IBAN/ISIN checksum validation (60000/60001) and the
   partner-state list (98200/98201) belong to the week-3 rule engine.
2. Week 3: rule engine — XSD, OECD rules (User Guide 4.0), the 67 ESTV codes mapped one by one
   with text and page; first pilot test upload (2.0 payload).
3. Week 4: local submission registry (SQLite: input row → DocRefId → message → outcome), then
   corrections/cancellations (Wegleitung Ziffer 6) and the status parser.
4. Week 5: CLI build/validate/correct, docs, page "what changes with 3.0".
5. Week 6: PyPI (`aeoi`, name free as of 2026-09-16), GitHub, Pyodide browser validator (lxml +
   rule engine only, no analytics, no server logs).

## Waiting on the owner

- PyPI account + API token to register the name.
- Pilot fiduciary: name, `ESTV-PublicKey.pem`, test-channel access.
- GitHub org/user and whether the repo is public from day one.
