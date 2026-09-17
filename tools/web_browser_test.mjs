// Real-browser test of web/index.html with Playwright (Chromium): serves web/ over HTTP, waits
// for the runtime, uploads a valid file, a broken file and a workbook (upper-case .XLSX), and
// asserts the privacy promise: after the file selection no network request at all, never a
// non-GET request, only the listed hosts during the boot, no CSP violation.
//
//   cd .local/pyodide-test && npm install playwright@1.49.1 && cd ../..
//   python -m build && python tools/build_web.py
//   PW_CHANNEL=chrome node tools/web_browser_test.mjs      # installed Chrome or msedge
//   (or: PLAYWRIGHT_BROWSERS_PATH=... npx playwright install chromium, then without PW_CHANNEL)
//
// Needs network access for cdn.jsdelivr.net, pypi.org and files.pythonhosted.org.

import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { mkdirSync, readFileSync } from "node:fs";

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
xml = build.build(sample_message(), "3.0", test=True).xml
open("${fx}/Test-report.xml", "w", encoding="utf-8").write(xml)
open("${fx}/Test-bad.xml", "w", encoding="utf-8").write(xml.replace("Beispiel AG", "Beispiel # AG"))
template.write_message(sample_message(), "${fx}/EXAMPLE.XLSX")
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
  const page = await browser.newPage();
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
  await page.goto(`http://127.0.0.1:${port}/index.html`);
  await ready;
  console.log("runtime ready; version", await page.locator("#ver").textContent());
  const bootRequests = requests.length;

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
  const good = await upload(join(fixtures, "Test-report.xml"));
  check("valid XML -> OK: " + good.split("\n")[0], good.startsWith("OK"));
  check("verdict card in the OK state", (await page.locator("#verdict").getAttribute("class")).includes("ok") && (await page.locator("#verdict-title").textContent()).length > 0);
  const bad = await upload(join(fixtures, "Test-bad.xml"));
  check("broken XML -> NOT OK with 50005", bad.startsWith("NOT OK") && bad.includes("[50005]"));
  const firstTitle = await page.locator(".finding.error .title").first().textContent();
  const firstFix = await page.locator(".finding.error .fix").first().textContent();
  check("finding card with German title and remedy", firstTitle === "Unzulässiges Zeichen" && firstFix.includes("#"));
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

  // language switch: page texts and finding titles change, the English report and the ready status survive
  for (const [lang, h1, ready, none] of [["it", "Verificare", "Pronto.", "Nessun rilievo"], ["fr", "Vérifier", "Prêt.", "Aucune constatation"], ["de", "CRS-Datei", "Bereit.", "Keine Befunde"]]) {
    await page.locator("#lang").selectOption(lang);
    const heading = await page.locator("h1").textContent();
    const st = await page.locator("#status").textContent();
    const rep = await resultText();
    const noFindings = await page.locator("#no-findings").textContent();
    check(`language ${lang}: heading, status, kept report, translated findings`, heading.startsWith(h1) && st.startsWith(ready) && rep === okSample && noFindings.startsWith(none));
  }

  const after = requests.slice(bootRequests);
  check(`no network request after the file selection (${after.length} after boot)`, after.length === 0);
  check("no non-GET request at all", requests.every((r) => r.method === "GET"));
  const hosts = [...new Set(requests.map((r) => r.host))].sort();
  const allowed = new Set([`127.0.0.1:${port}`, "cdn.jsdelivr.net", "pypi.org", "files.pythonhosted.org"]);
  check("only the listed hosts during boot: " + hosts.join(", "), hosts.every((h) => allowed.has(h)));
  check("no CSP violation reported by the browser", cspViolations.length === 0);
  if (cspViolations.length) console.log(cspViolations.slice(0, 3).join("\n"));
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
