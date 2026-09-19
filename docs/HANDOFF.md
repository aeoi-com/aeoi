# Handoff — state of the project (updated 2026-09-19)

Read this first in any new session. It is the memory of the project when the chat history is not
at hand.

## What we are building

`aeoi`: open toolkit that turns a flat table of reportable accounts into the XML files tax
administrations require for the automatic exchange of information — CRS (OECD XML Schema 3.0,
mandatory at the Swiss ESTV from 16.01.2027; 2.0 accepted until 14.12.2026), later CARF and FATCA.
Validates against the XSD, the OECD business rules and the portal rules, packages/encrypts for
upload, keeps a local registry of what was sent, builds corrections, parses the returned status.

Why: no open implementation exists (GitHub/PyPI: zero); the closed ones are priced per named
user or on request (competitor details are kept out of this public file). Swiss market:
~9'000 reporting FIs registered at the ESTV, mostly vehicles run by fiduciaries.

## Decisions taken

- Python first (xsdata models, lxml/xmlschema, pydantic domain), Rust only later for a WASM
  browser validator. Apache-2.0 core + DCO; PRO packs proprietary.
- Module order: CRS 3.0 for Switzerland → CARF 1.5 (Jan–Feb 2027) → portal packs BZSt, HMRC, ACD
  (verify each portal's envelope before promising) → FATCA/IDES last.
- Pricing (decided 19.09.2026, replaces the three flat bands): Basis free and complete; **Pro
  120 CHF per vehicle and year, minimum 900 CHF per organisation**, users unlimited, from 100
  vehicles on request - priced per vehicle so fiduciaries can re-bill it. Pro buys something
  tangible, not support alone: the **Prüfprotokoll** (PDF per check and per built message,
  shipped 19.09), Mandantenübersicht + batch over all vehicles (shipped 19.09 evening:
  `meldbar_pro.mandanten` - pairs `<stem>.xlsx` + `<stem>.sqlite`, `overview()` without side
  effects, `batch_build()` = check -> plan -> build -> package -> protocol per message, registries
  updated in place, `zip_outputs()` for browsers without the File System Access API; UI in
  `web/pro.js`, card `#mand-card`), support (2 working days, 1 in May-June), rule updates
  within 30 days, 1-hour onboarding. One-off **Begleitete erste Meldung** 450 CHF (1 h screen
  share, also without Pro). Software houses: a note (2'500 CHF/yr integration support; the
  library is Apache-2.0 anyway). Pilots get Pro free for the first year.
- **Pro is proprietary and lives in the private repository `aeoi-com/meldbar-pro`** (never in
  this repo, never in clear on the page). Delivery: one AES-256-GCM blob per licence at
  `web/pro/<blob_id>.bin`, blob id and key derived from the licence key `MB1-XXXXX-XXXXX-XXXXX-
  XXXXX` (HMAC / HKDF, mirrored in `web/pro.js` with WebCrypto, test vectors in the private
  tests); the page installs the decrypted wheel into Pyodide. `web/pro/` is git-ignored; the
  Pages workflow clones the private repository with a read-only deploy key (secret
  `PRO_DEPLOY_KEY`, set 19.09.2026; org setting "deploy keys" enabled for that) and copies
  `dist/pro/*.bin` - the blobs are tracked in the private repo, rebuilt and pushed after every
  licence change.
  Licences: `tools/issue_licence.py` appends to `licences/licences.json` (the only record of the
  keys), `tools/build_bundle.py` rebuilds every blob; expired keys (30-day grace) get no blob.
  Example key `MB1-TESTA-TESTB-TESTC-TESTD` is used by both test suites (unknown on a public
  deploy, active on a developer machine after `build_bundle.py --into ../aeoi/web`).
- Market research 19.09.2026 (kept out of this public file; see the owner's notes): the direct
  Swiss incumbent is a desktop product with a perpetual starter licence cheaper than three
  years of the old bands; hence the per-vehicle price and the tangible Pro contents.
- CARF for Switzerland: at the earliest 1.1.2027 (SIF FAQ 18.05.2026; parliament must approve
  the partner states first, the ESTV Wegleitung comes only after that) -> first Swiss CARF
  filings 2028. The "CARF 1.5 in Jan-Feb 2027" step of the module order is premature for CH:
  keep the generated models, build nothing until the Wegleitung exists.
- The pilot reporting FI is a prerequisite (portal access, `ESTV-PublicKey.pem`, test uploads).
  The pilot sends validation results (DocRefId + codes), never the file.
- Gates: mid-Dec 2026 developer signals in OR, **measurable ones only** (the page has no
  analytics by design, so "files validated in the browser" is not a signal): pypistats downloads
  without mirrors (after the 0.0.1 release), stars and issues from strangers, repository
  Insights → Traffic (unique visitors and cloners over 14 days, noted every week in
  `docs/TRAFFIC.md` because GitHub keeps no history), requests through associations - thresholds
  in `docs/TRAFFIC.md`; mid-Mar 2027 three pilots with real files validated on the ESTV test
  channel; 31 May 2027 three paid licences or one library licence; hard close 30 June 2027.
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
- Week-2 review fixes: `uid` optional (IN omitted, 70015), trustee-documented trusts
  (`trustee_documented_trust` flag -> `TDT=` prefix, 5.3.4), Anhang 7.2 character set enforced on
  every text field (50005), CRS702 refused until the registry exists (80010), header codes
  98004/98005/60015, ESTV-ID shape only a warning, joint-account consistency (3.0), duplicate
  DocRefId on rows (80000), no Contact in MessageSpec, `aeoi crs build` validates against the XSD
  before writing (XSDs shipped in `src/aeoi/xsd`, synced by `tools/generate_models.py`).
- Week 3 (started): partner states by reporting year from the SIF list, pinned in
  `src/aeoi/estv/partner_states.json` (116 states + 7 EU-agreement territories AX GF GP MQ YT RE
  MF from SIF footnote 6, "Stand per 25.08.2026"; pin = `table_sha256` of the canonical table,
  page hash only informational because the page is dynamic; refresh with
  `python tools/partner_states.py`), rules 98200/98201/98202 with the undocumented and
  controlling-person exceptions and messages that show the way out (US -> FATCA; CH-only
  controlling person of a CRS101 -> declare CRS102/CRS103); IBAN mod-97 and ISIN Luhn
  (60000/60001), IBAN/ISIN written normalised (no spaces, upper case) with an info note.
- Rules catalogue: every code of the Wegleitung with section, page, excerpt, status and the place
  in the code base that enforces it (`tools/build_rules_catalogue.py`); a test proves that every
  "implemented" code is referenced in code or tests.
- Status outcomes (`aeoi.estv.status`, CLI `aeoi estv status FILE`): parses an OECD CRS Status
  Message 2.0 (expected M2M format) or plain portal text pasted by the pilot into findings with
  code, DocRefIds, fields; looks each code up in the catalogue and flags findings on rules the
  toolkit claims to enforce as bugs. The real ESTV format is still open question 4.
- OECD status-message codes not listed by the ESTV are mapped in docs/ESTV-RULES.md: 50013
  (packaging by construction), 60011/60012 (CA-to-CA sorting, superseded by 98200-98202),
  60016 (= 60005), 70000/70002/70003/70012 (deleted by User Guide v3.0), 80009/80012-80015,
  90000-90002 (TIN, not applied by the ESTV), 99999.
- Week 4 (done): submission registry `aeoi.registry` (SQLite, one file per reporting FI, kept
  on the FI's machine; stores messages, DocSpecs with chains, account content for deletions,
  portal findings) and the workflow `aeoi.crs.submit`: `build_new` (CRS701/CRS703 with fresh
  identifiers, FI resent as OECD0 after the first message, 98009), `build_correction` (CRS702:
  OECD2 for changed rows by content hash, OECD3 via `--cancel`, CorrDocRefId = chain head,
  unchanged rows left out, new rows refused), `record_outcome` (accepted/rejected; a rejected
  correction frees its targets). CLI: `aeoi crs build --registry`, `aeoi crs correct`,
  `aeoi crs registry [--discard REF]`, `aeoi estv status --registry`. The 12 "registry" rules
  are implemented; catalogue: 59 implemented, 6 portal-only.
- Schema switch handled in the registry: each record stores the version it was sent in;
  "changed" is judged on the projection of that version (a 3.0 workbook does not make 2.0
  records look changed); deletions always start from the stored content (98204) and, built in
  3.0 for a 2.0 record, fill the new mandatory elements with the transitional values CRS900 /
  CRS1000 / CRS800 / CRS1100 / CRS1200. Corrections require the target message to be
  `accepted` (not merely built or submitted); the ReportingFI is resent (OECD0) only from an
  accepted message, otherwise OECD1 with a new DocRefId; `discarded` marks a built message that
  was never uploaded and frees its chain targets.
- Week 5 (in progress): `aeoi crs validate FILE.xml` (`aeoi.crs.validate` on top of
  `aeoi.crs.read_xml`, the inverse of the builder): XSD, header/DocSpec rules readable from the
  file (80004-80011, 98100, 98101, 60007-60010, 60013, 50010/50011 from the file name, the
  Wegleitung-header namespace case), character set on every text node, size limit, then the
  content rules through `check_message`; works on files from any tool, both versions.
  German pages for the pilot: `docs/de/ANLEITUNG.md` (step by step) and
  `docs/de/WAS-AENDERT-SICH-MIT-3.0.md` (dates, new mandatory elements, transitional values,
  online-form limits, header question), all statements cited from the Wegleitung / XSD.
- Week 5 review fixes: 80001 against the MessageRefId year, 98006 per the ESTV formula, one
  50005 per character, no traceback for non-schema files; guide: both key locations, install from
  the repository, weekly deletion of test messages.
- Week 6: browser validator `web/index.html` (Pyodide 0.27.7 - first from jsdelivr, since
  17.09.2026 vendored on the page's own origin, see below -,
  micropip installs xmlschema, xsdata==24.12 - 26.x needs typing-extensions>=4.12 while the
  Pyodide pydantic pins 4.11 -, openpyxl, and the aeoi wheel next to the page; file never leaves
  the browser, no analytics, no server side); `tools/build_web.py` copies the wheel;
  `tools/web_smoke.mjs` runs the same Python headlessly in Node (validate 4 s, workbook 1 s);
  `tools/web_browser_test.mjs` drives the real page with Playwright in the installed Chrome
  (`PW_CHANNEL=chrome`; the Playwright Chromium download hung twice on this machine) and passes:
  valid XML OK, broken XML 50005, upper-case .XLSX workbook OK, zero requests after the file
  selection, only the three listed hosts plus the page host during boot, GET only, no CSP
  violation. The page's CSP (`script-src 'self' cdn.jsdelivr.net 'wasm-unsafe-eval'`, SRI on
  pyodide.js) is enforced during the test; Pyodide boots under it without `'unsafe-eval'`.
  Because the CSP forbids eval, the test cannot use `page.evaluate`/`waitForFunction`: the page
  emits `console.info("aeoi:ready")` and `"aeoi:result …"` and the test waits on those console
  events (CDP, outside the CSP). Packaging: `python -m
  build` gives a 188 KB wheel with XSDs and JSON data, sdist trimmed of docs/sources; twine check
  passes; the wheel installs and runs in a clean venv. GitHub readiness: `.github/workflows/ci.yml`
  (tests on Linux/Windows, 3.11-3.13, ruff, build + twine + clean install, web smoke, DCO check on
  pull requests), `pages.yml` (publishes web/ to GitHub Pages), CHANGELOG.md, CONTRIBUTING.md (DCO).
- 217 tests: `.venv/Scripts/python -m pytest`; browser test 68 checks (incl. Pro activation with
  the example key, both Prüfprotokoll downloads and the Mandanten batch flow when the private
  blob is in `web/pro/` - `build_bundle.py --licences licences/licences.example.json --into
  ../aeoi/web` in the private repo).

## Verified facts to keep

- Wegleitung 3.3.1: CRS_Payload.xml → zip → AES-256-CBC (fresh IV, PKCS#7) → key+IV 48 bytes in
  RSA PKCS#1 v1.5 → zip {CRS_Payload, CRS_KEY}; test files start with "Test"; XML ≤ 100 MB,
  package ≤ 10 MB; XML must not be signed (50007).
- 65 ESTV rule codes (67 distinct five-digit numbers in the Wegleitung: 98999 is the range bound
  and 70012 only a change-log reference); catalogue with status and page in
  `src/aeoi/estv/rules_catalogue.json` / `docs/ESTV-RULES.md` (47 implemented, 12 waiting for the
  registry/corrections (0 since week 4: 59 implemented), 6 portal-only; plus OECD 50013/60011/60012 with origin "oecd"; sections
  are cumulative across pages and 50010/50011 keep both wordings); ESTV-specific range 98000-98999; ReportingFI cannot be corrected or
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
2. Week 3: done except the first pilot test upload (2.0 payload), which needs the pilot. Yearly
   maintenance: rerun `tools/partner_states.py` when the SIF list changes.
3. Week 4: done (registry, corrections, deletions, outcomes; see above). Open: the real ESTV
   outcome format (question 4) decides whether `aeoi estv status` can be fed automatically.
4. Week 5: validate + German pages done; the one-page summary for associations is
   `docs/de/KURZFASSUNG.md` (pricing bands from the decisions; "pilots pay nothing" is an
   assumption for the owner to confirm; contact and repository URL are placeholders), with
   Italian and French versions (`docs/it/RIASSUNTO.md`, `docs/fr/RESUME.md`) whose quotes come
   from the official FR/IT editions of the Technische Wegleitung (pinned in the manifest, not
   committed). The web page has a language switch (DE/FR/IT, `web/i18n.js`; choice kept in
   localStorage, no request). Design pass (17.09.2026): own design system (`web/styles.css`,
   Inter self-hosted under OFL in `web/fonts/`), boot stepper, drop zone, verdict card, stats
   with count-up, overview (holder-type ring, residence bars via `Intl.DisplayNames`), finding
   cards with title + remedy in the page language from `src/aeoi/estv/rule_titles.json`
   (`aeoi.estv.titles`; a test asserts every catalogue code and every code the engine emits has
   de/fr/it/en), technical message and official German wording behind a disclosure; built-in
   samples (valid, four errors, workbook), report download (blob:), copy, theme toggle.
   `aeoi.crs.overview.report_dict` is the JSON the page renders; `ValidationReport.message`
   carries the parsed content. Browser test: 16 checks incl. samples, download, three languages.
   Flow in the page (17.09.2026, after the review "registry as a file, browser only a cache"):
   `web/flow.js` + `aeoi.crs.workflow` (plan/build/record_outcome/registry_view); the registry
   is `institut.sqlite` chosen by the user - File System Access API on Chrome/Edge (handle kept
   in IndexedDB, one permission click per session), download after every change elsewhere and
   with `#nofsa` (the automated test); `sqlite3` must be loaded explicitly in Pyodide
   (`loadPackage("sqlite3")`); the ESTV public key is remembered in the registry (`settings`
   table); build produces correction + new message when the workbook implies both; productive
   builds need the registry, test builds do not. Browser test: 30 checks incl. the fallback flow
   (new registry, key, build, package + XML download, outcome accepted, changed workbook ->
   correction with a deletion, reopen the saved registry) and an outside-the-browser verification
   (inspect_package, decrypt with the test key, validate, DocTypeIndics, registry statuses).
   Same origin only (17.09.2026, review condition 2): `tools/build_web.py` now vendors the
   Pyodide core + the dependency closure of lxml/pydantic/micropip/cryptography/sqlite3 computed
   from the official `pyodide-lock.json` (13 packages, pruned lock written next to them, sha256
   checked against the lock) into `web/pyodide/`, and the pure-Python wheels (xmlschema,
   elementpath, xsdata==24.12, openpyxl, et_xmlfile; `pip download --no-deps`, installed with
   `deps=False`) into `web/wheels/`; downloads cached in `.local/vendor-cache`; all of it
   git-ignored and rebuilt by CI/Pages. `web/sw.js` (from `tools/sw.template.js`) precaches
   every file (~23 MB) so the page boots offline; `manifest.webmanifest` + SVG icons make it
   installable. CSP is now `'self'` only (`script-src 'self' 'wasm-unsafe-eval'`,
   `connect-src 'self'`); privacy text «nur diese Seite». Browser test: 31 checks - hosts seen
   during boot = the page's origin only, and a second page boots offline from the service worker.
   Messages in German (17.09.2026): `aeoi.messages.Msg` is a `str` subclass (English
   rendering, so every caller and test keeps working) that remembers its catalogue id and
   parameters and renders another language with `.text(lang)`; nested messages and lists of
   messages render recursively; `messages.json` has 136 entries (en + de, placeholders checked
   equal by a test, unused/missing ids checked against the code). Converted: model.py,
   validate.py, ids.py (format checks and character reasons), flat.py (InputProblem), the
   RegistryError / WorkflowError texts; `render(lang)` on both reports, `--lang de` on the CLI,
   the page renders in its language (German today; fr/it fall back to English until translated).
   17.09 (night): fr/it columns of `messages.json` filled for all 151 ids (catalogue test covers four
   languages); `--lang fr|it` on check/validate.
   Review 17.09 (evening): portal terms - «abgelehnt» (not «abgewiesen», the portal's own status
   word), «Berichtsjahr» for the MessageRefId year and «Meldezeitraum» for ReportingPeriod,
   «nicht dokumentiertes Konto», «Ansässigkeitsstaat»; headlines and labels of both reports are
   catalogue entries with singular|plural forms («NICHT OK: 1 Konto, Berichtsjahr 2026, CRS 3.0,
   2 Eingabeprobleme, 0 Fehler»); the portal status «Fehler» (Benutzeranleitung: unknown problem,
   upload again) is parsed as `Outcome.portal_error`, not a verdict: the message goes to
   `submitted` (open) with the note «Status «Fehler»: … noch einmal hochladen».
   Website (17.09.2026, evening): `tools/render_site.py` renders index/preise/ueber-uns/kontakt/
   impressum/datenschutz from shared fragments; `web/site.css` + `web/site.js` (language, theme,
   burger, reveal, counters, countdowns, scroll-driven horizontal steps, mailto contact form);
   `web/site-i18n.js` holds the de/fr/it copy. App at `app.html` (manifest start_url), shared
   header, samples hidden unless `#demo`. Content decisions to confirm with the owner: the Pro
   tier contents (support with priority in May-June, guaranteed rule updates, review of the first
   message, 1-hour onboarding) and the software-house licence contents are proposals; the About
   page claims only what is true (Zurich, built from the primary sources, small team) - no
   invented credentials, customers or numbers; contact address kontakt@meldbar.ch must exist;
   the imprint names "meldbar" without a legal-entity form. Browser test: 43 checks.
   Dark mode removed on the owner's request (light only; no theme toggle, no `aeoi-theme` key).
   AGB (`agb.html`, `web/site-i18n-agb.js`, de binding + fr/it courtesy): free part under Apache
   "as is", Pro contents defined (support within 2 working days, 1 in May-June; rule updates
   within 30 days of publication; one review of the first message = tool check + explanation;
   1-hour onboarding), no advice, customer responsible for content/deadlines/upload/registry,
   prices CHF per year in advance, 12-month term with auto-renewal, liability excluded for slight
   negligence and capped at one year's fee (Art. 100 OR reserved), Swiss law, Zurich. The
   provider is still "meldbar, Salvatorstrasse 8" - replace with the legal entity once it exists;
   have a Swiss lawyer read the AGB before the first paid contract.
   SEO basics (18.09.2026): canonical, Open Graph/Twitter (`web/og.png` from `tools/og_image.mjs`),
   JSON-LD (Organization with the Zurich address, WebSite, per-page type, SoftwareApplication
   with the CHF offers on home and pricing, FAQPage on pricing), `sitemap.xml` and `robots.txt`
   (pyodide/ and wheels/ disallowed) written by render_site, `404.html`, keyword titles. Still
   to do for search: one URL per language with hreflang (`/fr/`, `/it/`), an error-code page
   from rule_titles + catalogue, the 3.0 guide as a page; owner: Search Console and Bing
   verification tokens, Google Business Profile, links from associations, PyPI.
   Done 18.09 (evening): one URL per language - render_site evaluates the JS dictionaries with
   node (`load_i18n`), bakes fr/it texts into `web/fr/*.html` and `web/it/*.html` (regex over
   `data-i18n` elements; no nested same-name tags in the templates), assets referenced one level
   up (the CSP forbids <base>), hreflang de/fr/it/x-default on every page, sitemap with all 25
   URLs; site.js treats the page language as authoritative and the switch navigates to the
   sibling URL. `fehlercodes.html` (de/fr/it): all 68 catalogue codes with title and remedy in
   the page language, status (checked by meldbar / portal only / OECD), Wegleitung reference,
   official German wording behind a disclosure, client-side search, anchors `#50005`; linked
   from the home features and the footer. Browser test: 51 checks.
   Pilot hedges (18.09): the ESTV key loads as PEM or DER, key or certificate
   (`packaging.load_public_key`, stored as PEM); the 3.0 header exists in both variants (see
   OPEN-QUESTIONS 1) in build/submit/workflow/CLI/page; browser test builds the first message with
   the Wegleitung header and the correction with the OECD one (52 checks).
   Registry restore (18.09): `aeoi.crs.restore.restore(reg, files, status=, workbook=)` reads
   the sent XML files (`build.canonical_xml` + `read_xml.parse`), orders them by Timestamp,
   maps OECD1x to the productive DocTypeIndic with the test flag on the message, takes the key
   of a correction from its target record, of a new record from the workbook (`registry.identity`
   = account number + holder) or the account number; `Registry.register_message` accepts
   `created_at`, `status`, `status_source`, `fi_doc_type_indic` (an unknown OECD0 ReportingFI is
   stored so later messages resend it). `workflow.restore_registry`, `aeoi crs restore`, page
   block «Register verloren?» (`#restore-files`, multi-select incl. the workbook). `projected()`
   quantises amounts to 0.01 (a restored record hashes like its workbook row; also removes the
   1500 vs 1500.0 false "changed"). `plan()` blocks a "new" row whose identity is a valid record
   under a key the workbook no longer uses (`wf_key_renamed`). Tests: `tests/test_restore.py`
   (round trip with identical chain heads, fallback keys + guard, joint accounts, Wegleitung
   header + 2.0, duplicates/junk/mixed/clash, missing target, submitted status, CLI); browser
   test rebuilds a fresh registry from the two downloaded XML files and compares chain heads
   with the original (57 checks).
   Load test (18.09): `tools/web_load_test.mjs` (`AEOI_LOAD_N`, default 3'000; valid IBANs,
   2/3 persons with a payment, 1/3 entities with a controlling person) in Chrome on this
   machine: boot 8 s, validate the 5.3 MB XML 17 s, workbook check 4 s, plan against an empty
   registry +0 s, build + encrypt + register 21 s (registry 4.3 MB, package 0.2 MB), outcome
   1 s, changed workbook check + plan 9 s, re-plan after a cancel key 5 s, correction (300
   OECD2 + 1 OECD3) 12 s, restore from the two files 21 s; JS heap stays around 20 MB (Pyodide's
   WASM memory is separate); no page error. Consequences applied: `nextPaint()` before every
   long synchronous Python call so the busy state is visible, the cancel-key input is debounced
   (400 ms), the build button is disabled while a plan or build runs. Budgets in the script are
   generous (2-6x) so it doubles as a regression test on slower machines; it is not in CI.
   Partner states rechecked (18.09): the SIF page downloaded again still says "Stand per
   25.08.2026", 123 rows, identical `table_sha256`; every German name -> ISO code mapping read
   by eye (BQ, CK, IM, GL, FO, NC, MO, HK, KN, LC, VC, TC, KY, CN, RU correct), all 27 EU states
   in force 2017, the SIF change log matches the notes (25.08.2026 Trinidad und Tobago now
   reciprocal, 28.11.2025 Curaçao temporarily non-reciprocal, TT and UG in force 01.01.2026,
   GE/MD/UA 2025, KE/TH 2024), footnote texts 1-9 match `FOOTNOTES`, footnote 7 (Global Forum
   block) is attached to no state today. Only `retrieved` and the informational page hash
   changed. Next recheck: when the SIF page shows a newer "Stand per" (typically after the
   Federal Council adds states for 01.01.2027) - `python tools/partner_states.py`.
   Readability pass (18.09, after the question "does a compliance officer understand the
   output?"): finding card = code + title, location chips (account, controlling person, field
   label in the page language + template column via `FIELDS`/`fieldChip` in web/i18n.js and
   app.js), the specific message visible, «Was tun», then a `<details>` with the ESTV wording and
   the technical path; remedies of 50003/50005/50010/50011/50013/80002/98001/98006/98104 and the
   messages char_*/account_number_normalised/iban_invalid/isin_invalid/us_hint rewritten in
   plain language (de/fr/it/en). Remaining vocabulary is the Wegleitung's own (Rechtsträger,
   beherrschende Person, CRS101-103, OECD601) - a compliance officer's terms, kept on purpose.
   Not translated on purpose until
   the pilot confirms the German content: the two long German guides in fr/it.
   Excel template localised (17.09, night): `src/aeoi/crs/template_i18n.json` keyed by the English
   source string (column comments, ReadMe paragraphs, Codes sheet, headers) in de/fr/it;
   `template.tr()`, `write_template(path, lang=)`, `aeoi crs template --lang`, the app generates
   the template in the page language (`meldbar-vorlage-<lang>.xlsx`), and `tools/build_web.py`
   writes the four empty templates to `web/vorlage/` (git-ignored, precached, linked from the
   home page step 1 via `[data-vorlage]` whose href follows the language). Both workflows now
   `pip install dist/*.whl` before `build_web.py` (it imports the package).
5. Week 6: browser validator, packages and CI done locally; waiting on the owner for the PyPI
   token (upload 0.0.1) and the GitHub repository (push, enable Pages, replace the placeholder
   links in README/pyproject/docs/de/ANLEITUNG.md and web/index.html).

## Waiting on the owner


- PyPI account with 2FA; publishing goes through Trusted Publishing (`.github/workflows/release.yml`,
  pending publisher on PyPI: owner/aeoi, workflow release.yml, environment pypi), so no token is
  handed over; `git tag v0.0.1 && git push origin v0.0.1` releases.
- Pilot fiduciary: name, `ESTV-PublicKey.pem`, test-channel access.
- Done 17.09.2026: public repository `https://github.com/aeoi-com/aeoi` (org `aeoi-com`, commits
  under the pseudonymous account `aeoi-ch`), Pages enabled, PyPI pending publisher configured.
