// Real-browser test of web/index.html with Playwright (Chromium): serves web/ over HTTP, waits
// for the runtime, uploads a valid file, a broken file and a workbook (upper-case .XLSX), and
// asserts the privacy promise: after the file selection no network request at all, never a
// non-GET request, only the page's own origin during the boot, no CSP violation; then a second
// page goes offline and boots from the service worker cache.
//
//   cd .local/pyodide-test && npm install playwright@1.49.1 && cd ../..
//   python -m build && python tools/build_web.py
//   PW_CHANNEL=chrome node tools/web_browser_test.mjs      # installed Chrome or msedge
//   (or: PLAYWRIGHT_BROWSERS_PATH=... npx playwright install chromium, then without PW_CHANNEL)
//
// No network access needed: tools/build_web.py vendored the runtime and the wheels into web/.

import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const scratch = process.env.PYODIDE_DIR || join(root, ".local", "pyodide-test");
process.env.PLAYWRIGHT_BROWSERS_PATH ||= join(scratch, "browsers");
const { chromium } = createRequire(join(scratch, "package.json"))("playwright");

const fixtures = join(scratch, "fixtures");
mkdirSync(fixtures, { recursive: true });
const py = process.env.AEOI_PYTHON || join(root, ".venv", "Scripts", "python.exe");
const fx = fixtures.replace(/\\/g, "/");
await run(py, ["-c", `
from aeoi.crs import build, template
from aeoi.crs.example import sample_message
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
xml = build.build(sample_message(), "3.0", test=True).xml
open("${fx}/Test-report.xml", "w", encoding="utf-8").write(xml)
open("${fx}/Test-bad.xml", "w", encoding="utf-8").write(xml.replace("Beispiel AG", "Beispiel # AG"))
template.write_message(sample_message(), "${fx}/EXAMPLE.XLSX")
changed = sample_message()
changed.accounts[0].balance += 1
template.write_message(changed, "${fx}/EXAMPLE-changed.xlsx")
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)  # a test pair standing in for the ESTV key
open("${fx}/test-private.pem", "wb").write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
open("${fx}/ESTV-PublicKey.pem", "wb").write(key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
`]);

const port = 8765;
const server = spawn(py, ["-m", "http.server", String(port), "--bind", "127.0.0.1", "--directory", join(root, "web")], { stdio: "ignore" });
await new Promise((r) => setTimeout(r, 1500));

const checks = [];
function check(name, cond) {
  checks.push([name, !!cond]);
  console.log(`${cond ? "ok  " : "FAIL"} ${name}`);
}

// PW_CHANNEL=chrome|msedge drives a browser already installed on the machine (no download);
// unset, Playwright uses its own Chromium from PLAYWRIGHT_BROWSERS_PATH.
const browser = await chromium.launch(process.env.PW_CHANNEL ? { channel: process.env.PW_CHANNEL } : {});
try {
  // The page's CSP forbids eval, so no page.evaluate / waitForFunction: the page signals
  // readiness and results through console.info (CDP events, outside the CSP).
  const context = await browser.newContext(); // explicit: it must survive the first page's close
  const page = await context.newPage();
  const requests = [];
  const cspViolations = [];
  page.on("request", (req) => {
    const u = new URL(req.url());
    if (u.protocol === "blob:" || u.protocol === "data:") return; // in-browser only, cannot leave the machine
    requests.push({ host: u.host, method: req.method(), url: req.url() });
  });
  page.on("console", (msg) => {
    if (/Content Security Policy|Refused to/.test(msg.text())) cspViolations.push(msg.text());
  });
  page.on("pageerror", (err) => cspViolations.push("pageerror: " + err.message));
  const ready = page.waitForEvent("console", { predicate: (m) => m.text().startsWith("aeoi:ready"), timeout: 240000 });
  const swReady = page.waitForEvent("console", { predicate: (m) => m.text() === "aeoi:sw ready", timeout: 240000 });
  // #nofsa: the registry uses the download/upload fallback (native file pickers cannot be automated)
  await page.goto(`http://127.0.0.1:${port}/app.html#nofsa,demo`);
  await ready;
  console.log("runtime ready; version", await page.locator("#ver").textContent());
  let bootRequests = requests.length;

  // meldbar Pro: the loader is public, the pack is not. With the private bundle built into
  // web/pro/ (developer machine) the example key activates; on a public checkout it is unknown.
  // Either way: a same-origin GET only, before any file is selected.
  const proEvent = page.waitForEvent("console", { predicate: (m) => m.text().startsWith("aeoi:pro"), timeout: 120000 });
  await page.locator("#pro-key").fill("mb1 testa-testb testc testd");
  await page.locator("#pro-activate").click();
  const proText = (await proEvent).text();
  const proActive = proText === "aeoi:pro active valid";
  check("Pro key handled: " + proText + (proActive ? "" : " (no private bundle here)"), proActive || proText === "aeoi:pro unknown");
  check("Pro status line and form state agree", proActive ? (await page.locator("#pro-status").textContent()).includes("Muster Treuhand AG") && !(await page.locator("#pro-form").isVisible()) : (await page.locator("#pro-status").textContent()).includes("nicht bekannt"));
  const bootRequestsWithPro = requests.length;

  const resultText = () => page.locator("#out").textContent();
  async function upload(file) {
    const done = page.waitForEvent("console", { predicate: (m) => m.text().startsWith("aeoi:result"), timeout: 120000 });
    await page.locator("#file").setInputFiles(file);
    await done;
    return await resultText();
  }
  async function click(id) {
    const done = page.waitForEvent("console", { predicate: (m) => m.text().startsWith("aeoi:result"), timeout: 120000 });
    await page.locator(`#${id}`).click();
    await done;
    return await resultText();
  }
  bootRequests = bootRequestsWithPro;
  const good = await upload(join(fixtures, "Test-report.xml"));
  check("valid XML -> OK: " + good.split("\n")[0], good.startsWith("OK"));
  check("verdict card in the OK state", (await page.locator("#verdict").getAttribute("class")).includes("ok") && (await page.locator("#verdict-title").textContent()).length > 0);
  const bad = await upload(join(fixtures, "Test-bad.xml"));
  check("broken XML -> NICHT OK with 50005 (German headline)", bad.startsWith("NICHT OK") && bad.includes("[50005]"));
  const firstTitle = await page.locator(".finding.error .title").first().textContent();
  const firstFix = await page.locator(".finding.error .fix").first().textContent();
  const firstMsg = await page.locator(".finding.error .msg").first().textContent();
  check("finding card with German title, remedy and German message", firstTitle === "Unzulässiges Zeichen" && firstFix.includes("#") && firstMsg.includes("an Position 9: von der ESTV nicht zugelassen"));
  const wb = await upload(join(fixtures, "EXAMPLE.XLSX"));
  check("workbook (.XLSX) -> OK: " + wb.split("\n")[0], wb.startsWith("OK"));
  check("overview rendered (residence bars, holder ring)", (await page.locator("#ov-bars .row").count()) >= 2 && (await page.locator("#ov-ring circle.seg").count()) >= 1);

  // built-in samples and the report download (blob:, stays in the browser)
  const demo = await click("sample-bad");
  check("sample with errors -> four distinct rules", ["50005", "60000", "60002", "60014"].every((c) => demo.includes(`[${c}]`)));
  const dl = page.waitForEvent("download", { timeout: 30000 });
  await page.locator("#download").click();
  const saved = join(fixtures, "downloaded-report.txt");
  await (await dl).saveAs(saved);
  check("downloaded report equals the shown text", readFileSync(saved, "utf-8") === demo);
  const okSample = await click("sample-ok");
  check("valid sample -> OK", okSample.startsWith("OK"));
  if (proActive) {
    const pdl = page.waitForEvent("download", { timeout: 60000 });
    await page.locator("#protokoll").click();
    const pdfPath = join(fixtures, "protokoll-check.pdf");
    await (await pdl).saveAs(pdfPath);
    const pdf = readFileSync(pdfPath);
    check("Pro: Prüfprotokoll for the checked file downloaded (" + pdf.length + " bytes)", (await pdl).suggestedFilename().startsWith("Pruefprotokoll-") && pdf.subarray(0, 5).toString() === "%PDF-" && pdf.length > 5000);
  } else {
    check("Pro inactive: no protocol button", (await page.locator("#protokoll").count()) === 0);
  }

  // the Excel template generated in the browser, in the language of the page (German by default)
  const tplDl = page.waitForEvent("download", { timeout: 60000 });
  await page.locator("#template-download").click();
  const tpl = await tplDl;
  const tplPath = join(fixtures, tpl.suggestedFilename());
  await tpl.saveAs(tplPath);
  check("template downloaded in German: " + tpl.suggestedFilename(), tpl.suggestedFilename() === "meldbar-vorlage-de.xlsx" && readFileSync(tplPath).length > 10000);

  // language switch: page texts and finding titles change, the English report and the ready status survive
  for (const [lang, h1, ready, none] of [["it", "Verificare", "Pronto.", "Nessun rilievo"], ["fr", "Vérifier", "Prêt.", "Aucune constatation"], ["de", "CRS-Datei", "Bereit.", "Keine Befunde"]]) {
    await page.locator("#lang").selectOption(lang);
    const heading = await page.locator("h1").textContent();
    const st = await page.locator("#status").textContent();
    const rep = await resultText();
    const noFindings = await page.locator("#no-findings").textContent();
    check(`language ${lang}: heading, status, kept report, translated findings`, heading.startsWith(h1) && st.startsWith(ready) && rep.startsWith("OK") && noFindings.startsWith(none));
  }

  // ---- the reporting flow: registry file (fallback: download after every change), key,
  // build + encrypt, portal outcome, correction, reopen the saved registry ----
  const consoleEvent = (prefix) => page.waitForEvent("console", { predicate: (m) => m.text().startsWith(prefix), timeout: 120000 });
  async function withDownload(action, name) {
    const dl = page.waitForEvent("download", { timeout: 60000 });
    await action();
    const d = await dl;
    const path = join(fixtures, name || d.suggestedFilename());
    await d.saveAs(path);
    return path;
  }
  let regFile = await withDownload(async () => { const s = consoleEvent("aeoi:registry-saved"); await page.locator("#reg-new").click(); await s; }, "institut-0.sqlite");
  check("new registry created and downloaded", (await page.locator("#reg-status").textContent()).includes("0"));
  await upload(join(fixtures, "EXAMPLE.XLSX"));
  check("build card appears for a clean workbook", await page.locator("#build-card").isVisible());
  check("plan: 2 new accounts", (await page.locator("#plan .tag.new").textContent()).startsWith("2"));
  regFile = await withDownload(async () => { const s = consoleEvent("aeoi:registry-saved"); await page.locator("#key-file").setInputFiles(join(fixtures, "ESTV-PublicKey.pem")); await s; }, "institut-1.sqlite");
  check("ESTV key remembered in the registry", (await page.locator("#key-status").textContent()).length > 0 && (await page.locator("#key-status").getAttribute("class")).includes("msg-ok"));
  await page.locator("#build-header").selectOption("wegleitung"); // first message with the Wegleitung 5.3.1 header
  const builtMsg = consoleEvent("aeoi:built");
  regFile = await withDownload(async () => page.locator("#build").click(), "institut-2.sqlite");
  await page.locator("#build-header").selectOption("oecd"); // the correction with the OECD namespace
  const builtText = (await builtMsg).text();
  check("test message built and registered: " + builtText.slice(0, 40), builtText.includes("new:CH2026CH"));
  const pkgPath = await withDownload(async () => page.locator(".built .btn.primary").first().click());
  const xmlPath = await withDownload(async () => page.locator(".built .btn:not(.primary)").first().click());
  check("package and XML downloaded: " + pkgPath.split(/[\\/]/).pop(), /Test-CRS-2026-.*\.zip$/.test(pkgPath) && xmlPath.endsWith(".xml"));
  if (proActive) {
    const builtPdf = await withDownload(async () => page.locator(".built .btn.pro").first().click());
    const pdf = readFileSync(builtPdf);
    check("Pro: Prüfprotokoll for the built message downloaded (" + pdf.length + " bytes)", builtPdf.endsWith(".pdf") && pdf.subarray(0, 5).toString() === "%PDF-" && pdf.length > 5000);
  }
  check("registry lists the message as built, outcome card visible", (await page.locator("#reg-list .status.built").count()) === 1 && await page.locator("#outcome-card").isVisible());
  await page.locator("#outcome-text").fill("Validierungsbestätigung: Die Meldung wurde akzeptiert.");
  const outcomeMsg = consoleEvent("aeoi:outcome");
  regFile = await withDownload(async () => page.locator("#outcome-record").click(), "institut-3.sqlite");
  check("outcome recorded as accepted", (await outcomeMsg).text() === "aeoi:outcome accepted" && (await page.locator("#reg-list .status.accepted").count()) === 1);
  await upload(join(fixtures, "EXAMPLE-changed.xlsx"));
  check("plan after acceptance: 1 changed, 1 unchanged", (await page.locator("#plan .tag.changed").textContent()).startsWith("1") && (await page.locator("#plan .tag.unchanged").textContent()).startsWith("1"));
  await page.locator("#cancel-keys").fill("A2");
  check("plan with a cancelled account: 1 deletion", (await page.locator("#plan .tag.deleted").textContent()).startsWith("1"));
  const corrMsg = consoleEvent("aeoi:built");
  regFile = await withDownload(async () => page.locator("#build").click(), "institut-4.sqlite");
  check("correction built: " + (await corrMsg).text().slice(0, 45), (await corrMsg).text().includes("correction:CH2026CH"));
  const corrPath = await withDownload(async () => page.locator(".built .btn.primary").first().click());
  const corrXmlPath = await withDownload(async () => page.locator(".built .btn:not(.primary)").first().click());
  // reopen the last saved registry through the upload fallback: both messages are there
  await page.locator("#reg-file").setInputFiles(regFile);
  check("saved registry reopened: 2 messages (accepted + built)", (await page.locator("#reg-list .status.accepted").count()) === 1 && (await page.locator("#reg-list .status.built").count()) === 1);
  // the registry is lost: a fresh one is rebuilt from the two XML files (keys from the loaded workbook)
  await page.locator("#cancel-keys").fill("");
  await withDownload(async () => { const s = consoleEvent("aeoi:registry-saved"); await page.locator("#reg-new").click(); await s; }, "institut-5.sqlite");
  check("fresh registry: the restore block is offered, plan says 2 new", await page.locator("#restore-card").isVisible() && (await page.locator("#plan .tag.new").textContent()).startsWith("2"));
  const restoredMsg = consoleEvent("aeoi:restored");
  const restoredFile = await withDownload(async () => page.locator("#restore-files").setInputFiles([corrXmlPath, xmlPath]), "institut-6.sqlite");
  check("two files restored, none skipped: " + (await restoredMsg).text(), (await restoredMsg).text() === "aeoi:restored 2 0");
  check("restored messages are accepted; keys taken from the workbook", (await page.locator("#reg-list .status.accepted").count()) === 2 && (await page.locator("#restore-out .built").count()) === 2 && (await page.locator("#restore-out .built").first().textContent()).includes("2 Schlüssel aus der Vorlage"));
  check("plan against the restored registry: 1 unchanged, 1 new (the cancelled account)", (await page.locator("#plan .tag.unchanged").textContent()).startsWith("1") && (await page.locator("#plan .tag.new").textContent()).startsWith("1"));
  // ---- Mandantenübersicht + Stapelverarbeitung (Pro, file-input fallback -> one zip) ----
  if (proActive) {
    const mand = join(fixtures, "mandanten");
    mkdirSync(mand, { recursive: true });
    copyFileSync(join(fixtures, "EXAMPLE.XLSX"), join(mand, "Alpha-Trust.xlsx"));
    copyFileSync(join(fixtures, "EXAMPLE.XLSX"), join(mand, "Beta-Stiftung.xlsx"));
    copyFileSync(join(fixtures, "institut-1.sqlite"), join(mand, "Alpha-Trust.sqlite")); // empty registry with the ESTV key
    copyFileSync(join(fixtures, "institut-0.sqlite"), join(mand, "Gamma-Holding.sqlite")); // registry only
    check("Mandanten card visible with Pro, folder button hidden without FSA", await page.locator("#mand-card").isVisible() && !(await page.locator("#mand-folder").isVisible()));
    const ovMsg = consoleEvent("aeoi:mandanten");
    await page.locator("#mand-files").setInputFiles(["Alpha-Trust.xlsx", "Beta-Stiftung.xlsx", "Alpha-Trust.sqlite", "Gamma-Holding.sqlite"].map((n) => join(mand, n)));
    check("overview: 3 vehicles, 2 ready (test mode): " + (await ovMsg).text(), (await ovMsg).text() === "aeoi:mandanten overview 3 ready=2");
    check("overview table: 3 rows, Gamma has no workbook, Alpha shows the registry", (await page.locator("#mand-table tr.ready").count()) === 2 && (await page.locator("#mand-table tr").count()) === 4 && (await page.locator("#mand-table").textContent()).includes("Gamma-Holding"));
    await page.locator("#mand-mode").selectOption("prod");
    const ovProd = consoleEvent("aeoi:mandanten");
    check("productive mode: only the vehicle with a registry is ready: " + (await ovProd).text(), (await ovProd).text() === "aeoi:mandanten overview 3 ready=1");
    await page.locator("#mand-mode").selectOption("test");
    await consoleEvent("aeoi:mandanten");
    const builtMand = consoleEvent("aeoi:mandanten built");
    const zipPath = await withDownload(async () => page.locator("#mand-build").click());
    check("batch built 2 messages for 2 vehicles: " + (await builtMand).text(), (await builtMand).text() === "aeoi:mandanten built 2 vehicles=2 errors=0");
    const zipNames = readFileSync(zipPath).toString("latin1"); // central directory carries the names
    check("zip: outputs per vehicle, protocol PDFs, Alpha's registry under Register/: " + zipPath.split(/[\\/]/).pop(),
      /^Stapel-.*\.zip$/.test(zipPath.split(/[\\/]/).pop()) && zipNames.includes("Alpha-Trust/Test-CRS-") && zipNames.includes("Beta-Stiftung/Pruefprotokoll-") && zipNames.includes("Register/Alpha-Trust.sqlite") && zipNames.includes("manifest.json"));
    check("Alpha (key in registry) encrypted, Beta (no key) XML only", (await page.locator("#mand-out .built").count()) === 2 && (await page.locator("#mand-out").textContent()).includes("nicht verschlüsselt"));
    // the batch left Alpha with a pending message (in memory): quick verdict, then the portal's text
    await page.locator("#mand-table .quick .btn").first().waitFor({ timeout: 60000 }); // overview refreshed after the zip
    check("overview after the batch: Alpha pending with quick buttons", (await page.locator("#mand-table .mini.pending").count()) === 1 && (await page.locator("#mand-table .quick .btn").count()) === 2);
    const alphaRef = (await page.locator("#mand-out .built .ref").first().textContent()).split(" · ").pop().trim();
    const manual = consoleEvent("aeoi:mandanten manual");
    await page.locator("#mand-table .quick .btn").nth(1).click(); // ✗ abgelehnt
    check("quick verdict recorded: " + (await manual).text(), (await manual).text() === "aeoi:mandanten manual rejected" && await page.locator("#mand-save").isVisible());
    await page.locator("#mand-table .mini.rejected").first().waitFor({ timeout: 60000 });
    await page.locator("#mand-oc-text").fill(`Validierungsbestätigung: Die Meldung ${alphaRef} wurde akzeptiert.`);
    const oc = consoleEvent("aeoi:mandanten outcomes");
    await page.locator("#mand-oc-record").click();
    check("pasted portal text matched by MessageRefId and recorded: " + (await oc).text(), (await oc).text() === "aeoi:mandanten outcomes 1 unmatched=0" && (await page.locator("#mand-oc-out .built").textContent()).includes("accepted"));
    await page.locator("#mand-table .mini.accepted").first().waitFor({ timeout: 60000 });
    check("Alpha now accepted, nothing pending", (await page.locator("#mand-table .mini.accepted").count()) === 1 && (await page.locator("#mand-table .mini.pending").count()) === 0);
    const regZip = await withDownload(async () => page.locator("#mand-save").click());
    check("changed registries downloaded as one zip: " + regZip.split(/[\\/]/).pop(), /^Register-.*\.zip$/.test(regZip.split(/[\\/]/).pop()) && readFileSync(regZip).toString("latin1").includes("Register/Alpha-Trust.sqlite") && !(await page.locator("#mand-save").isVisible()));
  }

  // verify the encrypted packages and the registry outside the browser
  const verify = join(fixtures, "verify.txt");
  await run(py, ["-c", `
from aeoi.estv import packaging
from aeoi.crs import validate
from aeoi.registry import Registry
from cryptography.hazmat.primitives import serialization
import re
priv = serialization.load_pem_private_key(open(r"${fixtures}/test-private.pem", "rb").read(), password=None)
pub = packaging.load_public_key(open(r"${fixtures}/ESTV-PublicKey.pem", "rb").read())
out = []
for path, expect in ((r"${pkgPath}", ["OECD11", "OECD11", "OECD11"]), (r"${corrPath}", ["OECD10", "OECD12", "OECD13"])):
    data = open(path, "rb").read()
    name = path.replace(chr(92), "/").rsplit("/", 1)[-1]
    insp = packaging.inspect_package(data, public_key=pub, file_name=name, test=True)
    xml = packaging.unpackage(data, priv)
    open(r"${fixtures}/Test-unpacked.xml", "wb").write(xml)
    rep = validate.validate_file(r"${fixtures}/Test-unpacked.xml", test=True)
    indics = re.findall(r"<stf:DocTypeIndic>(OECD1\\d)</stf:DocTypeIndic>", xml.decode())
    header = "wegleitung" if b'xmlns:crs="urn:oecd:ties:crs:v2"' in xml and b'version="3.0"' in xml else "oecd"
    out.append(f"{name}: inspect={'ok' if not insp.problems else insp.problems} validate={'OK' if rep.ok else rep.render()} indics={indics} expected={expect} header={header} {'ok' if indics == expect else 'MISMATCH'}")
with Registry(r"${regFile}") as reg:
    statuses = [m['status'] for m in reg.messages()]
    out.append(f"registry: {statuses} key={'yes' if reg.get_setting('estv_public_key_pem') else 'no'}")
    heads = {(h.account_key, h.doc_ref_id, h.content_sha256, h.doc_type_indic) for h in reg.chain_heads(year=2026, test=True)}
with Registry(r"${restoredFile}") as reg:
    restored = {(h.account_key, h.doc_ref_id, h.content_sha256, h.doc_type_indic) for h in reg.chain_heads(year=2026, test=True)}
    out.append(f"restored: {'same chain heads' if restored == heads else 'DIFFERENT ' + str(restored ^ heads)} ({len(restored)} head(s), {reg.conn.execute('select count(*) from records').fetchone()[0]} records)")
open(r"${verify}", "w", encoding="utf-8").write(chr(10).join(out))
`]);
  const verifyText = readFileSync(verify, "utf-8");
  console.log(verifyText.split("\n").map((l) => "     " + l).join("\n"));
  const lines = verifyText.split(/\r?\n/);
  check("packages decrypt to valid test files with the right DocTypeIndics", lines.slice(0, 2).every((l) => l.includes("inspect=ok") && l.includes("validate=OK") && l.trim().endsWith(" ok")));
  check("first message carries the Wegleitung 5.3.1 header, the correction the OECD namespace", lines[0].includes("header=wegleitung") && lines[1].includes("header=oecd"));
  check("saved registry: accepted + built, key remembered", verifyText.includes("['accepted', 'built'] key=yes"));
  check("restored registry has the same chain heads as the original: " + (lines[3] || ""), lines[3].includes("same chain heads") && lines[3].includes("(1 head(s), 5 records)"));

  const after = requests.slice(bootRequests);
  check(`no network request after the file selection (${after.length} after boot)${after.length ? ": " + after.map((r) => r.url).join(", ") : ""}`, after.length === 0);
  check("no non-GET request at all", requests.every((r) => r.method === "GET"));
  const hosts = [...new Set(requests.map((r) => r.host))].sort();
  check("only the page's own origin, ever: " + hosts.join(", "), hosts.length === 1 && hosts[0] === `127.0.0.1:${port}`);
  check("no CSP violation reported by the browser", cspViolations.length === 0);
  if (cspViolations.length) console.log(cspViolations.slice(0, 3).join("\n"));

  // ---- the marketing pages: home, pricing, contact; language switch; phone navigation ----
  const site = await context.newPage();
  const siteHosts = new Set();
  const siteErrors = [];
  site.on("request", (r) => { const u = new URL(r.url()); if (!["blob:", "data:"].includes(u.protocol)) siteHosts.add(u.host); });
  site.on("pageerror", (e) => siteErrors.push(e.message));
  site.on("console", (m) => { if (/Content Security Policy|Refused to/.test(m.text())) siteErrors.push(m.text()); });
  await site.goto(`http://127.0.0.1:${port}/index.html`);
  await site.waitForTimeout(600);
  check("home: hero headline in German", (await site.locator(".hero-h1").textContent()).trim().startsWith("CRS-Meldungen"));
  const days = await site.locator("[data-until]").first().textContent();
  check("home: live countdown to 16.01.2027 shows a number (" + days + ")", /^\d+$/.test(days.trim()));
  check("home: five steps, six features, three plans", (await site.locator(".step-card").count()) === 5 && (await site.locator(".feature").count()) === 6 && (await site.locator(".plan-card").count()) === 3);
  const tplLink = site.locator("[data-vorlage]").first();
  const tplStatus = (await site.request.get(`http://127.0.0.1:${port}/` + (await tplLink.getAttribute("href")))).status();
  check("home: static template link answers 200 (" + (await tplLink.getAttribute("href")) + ")", tplStatus === 200);
  await site.locator("#lang").selectOption("it");
  check("home: Italian after the language switch", (await site.locator(".hero-h1").textContent()).trim().startsWith("Comunicazioni") && (await site.locator(".site-nav a").first().textContent()) === "Funzioni");
  check("home: template link follows the language", (await tplLink.getAttribute("href")) === "vorlage/meldbar-vorlage-it.xlsx");
  await site.locator("#lang").selectOption("de");
  await site.goto(`http://127.0.0.1:${port}/preise.html`);
  check("pricing page: three plans, five FAQ entries, per-vehicle price", (await site.locator(".plan-card").count()) === 3 && (await site.locator(".faq details").count()) === 5 && (await site.locator(".plan-card.featured .price").textContent()).includes("120 CHF"));
  await site.goto(`http://127.0.0.1:${port}/kontakt.html`);
  check("contact page: form without a server (mailto)", (await site.locator("#contact-form").getAttribute("data-to")) === "kontakt@meldbar.ch");
  for (const p of ["ueber-uns.html", "impressum.html", "datenschutz.html", "agb.html"]) {
    const r = await site.goto(`http://127.0.0.1:${port}/${p}`);
    check(`${p} answers 200 with the footer address`, r.status() === 200 && (await site.locator(".foot-bottom").textContent()).includes("Salvatorstrasse 8, 8050 Zürich"));
  }
  // one URL per language: /fr/ and /it/ are pre-rendered, hreflang links point at each other,
  // the language switch navigates between them
  await site.goto(`http://127.0.0.1:${port}/fr/index.html`);
  await site.waitForTimeout(400);
  check("fr/: French hero, html lang=fr, four hreflang links, assets one level up", (await site.locator(".hero-h1").textContent()).trim().startsWith("Déclarations") && (await site.locator("html").getAttribute("lang")) === "fr" && (await site.locator('link[rel="alternate"][hreflang]').count()) === 4 && (await site.locator('link[rel="stylesheet"][href="../styles.css"]').count()) === 1);
  await site.goto(`http://127.0.0.1:${port}/fr/preise.html`);
  await site.waitForTimeout(300);
  await Promise.all([site.waitForURL(/\/it\/preise\.html$/), site.locator("#lang").selectOption("it")]);
  check("language switch on /fr/preise.html navigates to /it/preise.html in Italian", (await site.locator("h1").textContent()).trim() === "Prezzi");
  await site.locator("#lang").selectOption("de");
  await site.waitForURL((u) => u.pathname === "/preise.html");
  // the error-code page: every catalogue code, search filter, anchors
  await site.goto(`http://127.0.0.1:${port}/fehlercodes.html`);
  await site.waitForTimeout(300);
  const codeCards = await site.locator("article.fc").count();
  await site.locator("#fc-search").fill("IBAN");
  await site.waitForTimeout(200);
  const visible = await site.locator("article.fc:not(.hidden)").count();
  check(`error-code page: ${codeCards} codes, search "IBAN" leaves ${visible}, #50005 anchor`, codeCards >= 65 && visible >= 1 && visible < codeCards && (await site.locator("article[id='50005']").count()) === 1);
  await site.goto(`http://127.0.0.1:${port}/it/fehlercodes.html`);
  check("it/fehlercodes: Italian titles, German official wording kept", (await site.locator("article.fc .title").first().textContent()).startsWith("File non") && (await site.locator("article.fc blockquote").first().textContent()).includes("Datei"));
  check("marketing pages: own origin only, no page error", siteHosts.size === 1 && siteHosts.has(`127.0.0.1:${port}`) && siteErrors.length === 0);
  if (siteErrors.length) console.log(siteErrors.slice(0, 3).join("\n"));
  await site.close();
  const phoneCtx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const phone = await phoneCtx.newPage();
  await phone.goto(`http://127.0.0.1:${port}/index.html`);
  await phone.locator(".burger").click();
  check("phone: burger opens the navigation", await phone.locator(".mobile-nav.open").isVisible() && (await phone.locator(".mobile-nav a").count()) >= 5);
  await phoneCtx.close();

  // offline: the service worker precached the app during the first visit
  await swReady;
  await page.close();
  await context.setOffline(true);
  const page2 = await context.newPage();
  const ready2 = page2.waitForEvent("console", { predicate: (m) => m.text().startsWith("aeoi:ready"), timeout: 240000 });
  await page2.goto(`http://127.0.0.1:${port}/app.html#nofsa,demo`);
  await ready2;
  const done2 = page2.waitForEvent("console", { predicate: (m) => m.text().startsWith("aeoi:result"), timeout: 120000 });
  await page2.locator("#sample-ok").click();
  await done2;
  check("offline: boots from the service worker cache and checks a file", (await page2.locator("#out").textContent()).startsWith("OK"));
  await context.setOffline(false);
  await page2.close();

  // a deploy while the app is in use: a new sw.js takes over and the page asks for one reload
  const swPath = join(root, "web", "sw.js");
  const swOriginal = readFileSync(swPath, "utf-8");
  writeFileSync(swPath, swOriginal.replace(/const CACHE = "aeoi-[^"]+";/, 'const CACHE = "aeoi-test-update";'));
  try {
    const page3 = await context.newPage();
    const newVersion = page3.waitForEvent("console", { predicate: (m) => m.text() === "aeoi:sw new-version", timeout: 120000 });
    await page3.goto(`http://127.0.0.1:${port}/app.html#nofsa,demo`);
    await newVersion;
    check("update banner after a new service worker took over", await page3.locator("#update").isVisible());
    await page3.close();
  } finally {
    writeFileSync(swPath, swOriginal);
  }
} finally {
  await browser.close();
  server.kill();
}
const ok = checks.every(([, c]) => c);
console.log(ok ? "BROWSER TEST OK" : "BROWSER TEST FAILED");
process.exit(ok ? 0 : 1);

function run(cmd, args) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: "inherit" });
    p.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`${cmd} exited ${code}`))));
  });
}
