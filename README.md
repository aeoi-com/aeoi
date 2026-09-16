# aeoi

Open toolkit for Automatic Exchange of Information reporting: **CRS** (OECD XML Schema 2.0 and 3.0),
**CARF** (1.5) and, later, **FATCA**. Swiss ESTV AIA portal first; other portals as rule packs.

Status: pre-alpha, week 2. What exists today:

- Typed Python models generated from the pinned OECD XSDs (`src/aeoi/schemas/`): CRS 2.0, CRS 3.0,
  CRS Status Message 2.0, CARF 1.5, CARF Status Message 1.1. Regenerate with
  `python tools/generate_models.py`.
- **Flat input format** (`docs/FLAT-FORMAT.md`): an Excel workbook or CSV folder with the sheets
  ReportingFI, Accounts, ControllingPersons, Payments; generated template with drop-downs and a
  `Codes` sheet (`aeoi crs template`).
- **Domain model and checks** (`aeoi.crs.model`): every 3.0 field, version-aware validation with
  talking errors (location + ESTV rule number) for both 2.0 and 3.0.
- **Builder** (`aeoi.crs.build`): domain -> CRS XML 2.0 or 3.0, valid against the OECD XSD;
  3.0 written in `urn:oecd:ties:crs:v3` only; ESTV header rules (5.3.2) applied.
- ESTV transfer package (`aeoi.estv.packaging`): `CRS_Payload.xml` -> zip -> AES-256-CBC ->
  RSA PKCS#1 v1.5 key blob -> `CRS_Payload` + `CRS_KEY` zip, with the 100 MB / 10 MB limits and
  the `Test*.zip` rule (Technische Wegleitung AIA, Ziffer 3.3.1 and 4.1.1).
- ESTV identifiers and character set (`aeoi.estv.ids`): MessageRefId, DocRefId, Anhang 7.2.
- Test corpus: the five annex examples of the Technische Wegleitung (2.0), validated against the
  OECD schema and round-tripped through the models; a complete 3.0 example built by construction.

Not yet: the full rule engine (67 ESTV codes with partner-state list and IBAN/ISIN checksums),
the local submission registry, corrections, the status-message parser, the browser validator.

## Why

From 1 January 2027 the amended CRS applies and every reporting financial institution must use the
OECD CRS XML Schema 3.0 (ESTV: 2.0 accepted until 14.12.2026, only 3.0 from 16.01.2027). There is
no open implementation of CRS, CARF or FATCA reporting; the closed ones are priced per named user.

## Quick start (development)

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/python -m pytest
```

From an Excel workbook to an ESTV test package (public key: `ESTV-PublicKey.pem` from the AIA
application):

```bash
aeoi crs template --out template.xlsx            # empty template (add --example for invented data)
aeoi crs check    --input filled.xlsx --version 3.0
aeoi crs build    --input filled.xlsx --version 3.0 --out report.xml --test                   --key ESTV-PublicKey.pem --package Test-report.zip
aeoi estv inspect Test-report.zip --key ESTV-PublicKey.pem --test
```

Until 14.12.2026 the ESTV accepts only schema 2.0 (`--version 2.0`); from 16.01.2027 only 3.0.

## Sources

All schemas and guidance documents are pinned with SHA-256 in [docs/SOURCES.md](docs/SOURCES.md).
Open questions for the pilot institution are in [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md).

## Data protection

The toolkit runs on the reporting institution's machine. No account-holder data leaves it; the
browser validator (planned) runs client-side with no analytics and no server-side logs.

## Licence

Apache-2.0. Contributions require a Developer Certificate of Origin sign-off (`git commit -s`).
