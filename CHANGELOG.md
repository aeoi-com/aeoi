# Changelog

All notable changes to aeoi. Dates are the day the work was completed.

## Unreleased

## 0.0.1 - 2026-09-16

First working version, CRS for the Swiss ESTV portal.

- Typed models generated from the pinned OECD XSDs: CRS 2.0, CRS 3.0, CRS Status Message 2.0,
  CARF 1.5, CARF Status Message 1.1 (`tools/generate_models.py`; Address_Type field-order patch).
- Flat input format (Excel workbook or CSV folder) with a generated template, drop-downs, a
  Codes sheet and a ReadMe; contract in `docs/FLAT-FORMAT.md`.
- Domain model with version-aware checks and talking errors (location + ESTV rule number);
  builder to CRS 2.0 or 3.0 XML, valid against the OECD schema, 3.0 in `urn:oecd:ties:crs:v3`.
- ESTV specifics: transfer package (zip + AES-256-CBC + RSA PKCS#1 v1.5), MessageRefId/DocRefId
  rules, Anhang 7.2 character set, partner states by reporting year from the pinned SIF list
  (116 states + 7 EU-agreement territories), IBAN mod-97 and ISIN Luhn checks.
- Rules catalogue: 65 ESTV codes with section, page, excerpt and enforcing location
  (`docs/ESTV-RULES.md`): 59 implemented, 6 portal-only; OECD 50013/60011/60012 mapped.
- Submission registry (SQLite on the FI's machine) with new messages, corrections (OECD2),
  deletions (OECD3), correction chains, nil reports, outcomes, schema-switch handling with the
  OECD transitional values, `discarded` state.
- Outcome parser for OECD CRS Status Message 2.0 and pasted portal text.
- `aeoi crs validate FILE.xml` for files from any tool (2.0 and 3.0).
- Browser validator (`web/`, Pyodide, no server side, no analytics).
- German pages for reporting FIs: `docs/de/ANLEITUNG.md`, `docs/de/WAS-AENDERT-SICH-MIT-3.0.md`.
- CLI: `aeoi crs template | check | build | correct | validate | registry`,
  `aeoi estv package | inspect | status`.
