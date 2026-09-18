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

- **Rule engine**: 59 of the 65 ESTV rules enforced before the file leaves the machine
  (`docs/ESTV-RULES.md`), partner states by year from the pinned SIF list, IBAN/ISIN checksums.
- **Submission registry** (`aeoi.registry`, SQLite on the FI's machine) and workflow
  (`aeoi.crs.submit`): new messages, corrections (OECD2), deletions (OECD3), correction chains,
  nil reports, outcomes; `aeoi crs correct`, `aeoi crs registry`, `aeoi estv status --registry`.
- **Outcome parser** (`aeoi.estv.status`): OECD CRS Status Message 2.0 or pasted portal text,
  every code explained from the catalogue.
- **Validator for any file** (`aeoi crs validate report.xml`): schema, header and DocSpec rules,
  character set, content rules - for XML produced by this or another tool, 2.0 and 3.0.
- **Messages in German** (`--lang de` on `check` and `validate`, automatic on the page): every
  check message is a catalogue entry (`src/aeoi/messages.json`, en + de, same placeholders,
  tested for completeness); English stays the reference the tests read.
- **German user pages** for reporting FIs and fiduciaries: `docs/de/ANLEITUNG.md`,
  `docs/de/WAS-AENDERT-SICH-MIT-3.0.md` and the one-page `docs/de/KURZFASSUNG.md` for associations,
  the latter also in Italian (`docs/it/RIASSUNTO.md`) and French (`docs/fr/RESUME.md`), quoting
  the official editions of the ESTV guidance in those languages.

Not yet: the pilot's first test upload (needs a registered FI), CARF.

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
aeoi crs build    --input filled.xlsx --version 3.0 --out report.xml --test --key ESTV-PublicKey.pem --package Test-report.zip
aeoi estv inspect Test-report.zip --key ESTV-PublicKey.pem --test
```

Until 14.12.2026 the ESTV accepts only schema 2.0 (`--version 2.0`); from 16.01.2027 only 3.0.

With a registry (recommended: it is what makes corrections possible):

```bash
aeoi crs build   --input filled.xlsx --version 3.0 --out m1.xml --registry fi.sqlite
aeoi estv status outcome.txt --registry fi.sqlite --message CH2026CH...   # after the portal answered
aeoi crs correct --input fixed.xlsx --version 3.0 --out m2.xml --registry fi.sqlite --cancel A7
aeoi crs registry --registry fi.sqlite
```

The registry file contains the account data needed to build deletions: keep it next to the
workbook, back it up, never send it. A lost registry is rebuilt from the XML files that were
uploaded (`aeoi crs restore --registry new.sqlite sent1.xml sent2.xml --input filled.xlsx`, or
the «Register verloren?» block of the app): the identifiers are in the files, the workbook
supplies the account keys.

## Browser validator

Online at https://meldbar.ch/ - marketing site (home, pricing, about, contact, imprint, privacy;
`tools/render_site.py`, texts in `web/site-i18n.js`, de/fr/it) with the app at
https://meldbar.ch/app.html (GitHub Pages, custom domain; the old address aeoi-com.github.io/aeoi redirects).

`web/index.html` is a static page that runs the validator in the browser with Pyodide: drop a
CRS XML file or a filled workbook and get the same checks as `aeoi crs validate` / `aeoi crs check`,
rendered as a verdict card, an overview of the message (holders, residence countries, balances)
and one card per finding with a title and a remedy in German, French or Italian
(`src/aeoi/estv/rule_titles.json`), the technical message and the official ESTV wording behind
a disclosure. Built-in samples, report download, light/dark theme, self-hosted Inter font.
Everything the page needs - the Pyodide runtime, the packages, the wheels, the fonts - is served
from the page's own origin (`tools/build_web.py` vendors it; nothing else is ever contacted), a
service worker keeps it available offline after the first visit, and the page can be installed
as an app from the browser.

The page also runs the whole reporting flow without an installation: download the empty
template, check the filled workbook, open or create the **registry file** (the state - on Chrome
and Edge it is rewritten in place through the File System Access API, elsewhere it is downloaded
after every change), choose the ESTV public key once (remembered in the registry), build the
message(s) the registry implies (new records, corrections, deletions - `aeoi.crs.workflow`),
download the encrypted package for the AIA portal, and record the portal's answer. Productive
messages need an open registry; test messages do not.
The file never leaves the browser; the page has no analytics and no server side. Build it with
`python -m build && python tools/build_web.py` (downloads the runtime once into `.local/vendor-cache`); `node tools/web_smoke.mjs` runs the same code
headlessly (see the script header for the one-time Pyodide setup);
`PW_CHANNEL=chrome node tools/web_browser_test.mjs` drives the real page in an installed Chrome
or Edge with the page's Content-Security-Policy enforced and asserts that no request leaves the
browser after the file selection. CI publishes the page to GitHub Pages once Pages is enabled
for the repository.

## Sources

All schemas and guidance documents are pinned with SHA-256 in [docs/SOURCES.md](docs/SOURCES.md).
Open questions for the pilot institution are in [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md).

## Data protection

The toolkit runs on the reporting institution's machine. No account-holder data leaves it; the
browser validator runs client-side with no analytics and no server-side logs.

## Licence

Apache-2.0. Contributions require a Developer Certificate of Origin sign-off (`git commit -s`).
