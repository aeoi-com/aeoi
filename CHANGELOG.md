# Changelog

All notable changes to aeoi. Dates are the day the work was completed.

## Unreleased

- Excel template in German, French and Italian (column comments, ReadMe, Codes sheet):
  `aeoi crs template --lang de|fr|it`, the app generates it in the page language, and
  `tools/build_web.py` publishes the four empty templates as static downloads (`web/vorlage/`),
  linked from the home page.
- Check and workflow messages rendered in French and Italian (catalogue complete in four
  languages); `--lang fr|it` on `check` and `validate`.

## 0.0.1 - 2026-09-17

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
- Browser validator (`web/`, Pyodide, no server side, no analytics; Content-Security-Policy
  and SRI on the page, verified in a real browser: no request after the file selection); page
  texts in German, French and Italian (`web/i18n.js`); findings with a title and a remedy per
  rule code in de/fr/it/en (`aeoi.estv.titles`, `rule_titles.json`), overview of the message
  (`aeoi.crs.overview`), built-in samples, report download, light/dark theme; the full
  reporting flow in the page: registry file (File System Access API or download fallback),
  template download, build + encrypt with the remembered ESTV key, portal outcome
  (`aeoi.crs.workflow`; registry `settings` table); runtime, packages and wheels vendored on
  the page's own origin, service worker for offline use, installable (web app manifest), CSP
  `'self'` only.
- Website meldbar.ch: home page with scroll effects (live countdown to 16.01.2027 and 30.06.2027,
  feature cards, scroll-driven horizontal steps, privacy diagram, pricing teaser), pages for
  pricing, about, contact (mailto, no server), imprint and privacy policy, in de/fr/it; the app
  moved to `app.html`, built-in samples only with `#demo`; palette aligned to the logo.
- Message catalogue (`aeoi.messages`, `messages.json`): every check, input, registry and workflow
  message is a `Msg` - an English string that renders in German on request; reports take
  `lang`, the CLI `--lang de`, the page shows German messages.
- German pages for reporting FIs: `docs/de/ANLEITUNG.md`, `docs/de/WAS-AENDERT-SICH-MIT-3.0.md`.
- CLI: `aeoi crs template | check | build | correct | validate | registry`,
  `aeoi estv package | inspect | status`.
