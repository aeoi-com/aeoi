// Real-browser test of web/index.html with Playwright (Chromium): serves web/ over HTTP, waits
// for the runtime, uploads a valid file, a broken file and a workbook (upper-case .XLSX), and
// asserts the privacy promise: after the file selection no network request at all, never a
// non-GET request, only the listed hosts during the boot, no CSP violation.
//
//   cd .local/pyodide-test && npm install playwright@1.49.1
//   PLAYWRIGHT_BROWSERS_PATH=$PWD/browsers npx playwright install chromium
//   cd ../.. && python -m build && python tools/build_web.py && node tools/web_browser_test.mjs
//
// Needs network access for cdn.jsdelivr.net, pypi.org and files.pythonhosted.org.

import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { mkdirSync } from "node:fs";

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

const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  const requests = [];
  const cspViolations = [];
  page.on("request", (req) => requests.push({ host: new URL(req.url()).host, method: req.method(), url: req.url() }));
  page.on("console", (msg) => {
    if (/Content Security Policy|Refused to/.test(msg.text())) cspViolations.push(msg.text());
  });
  await page.goto(`http://127.0.0.1:${port}/index.html`);
  await page.waitForFunction(() => document.getElementById("status").textContent.startsWith("Bereit"), null, { timeout: 240000 });
  console.log("runtime ready; version", await page.textContent("#ver"));
  const bootRequests = requests.length;

  async function upload(id, file) {
    await page.setInputFiles(`#${id}`, file);
    await page.waitForFunction(() => !document.getElementById("out").textContent.startsWith("Prüfung läuft"), null, { timeout: 120000 });
    return await page.textContent("#out");
  }
  const good = await upload("xml", join(fixtures, "Test-report.xml"));
  check("valid XML -> OK: " + good.split("\n")[0], good.startsWith("OK"));
  const bad = await upload("xml", join(fixtures, "Test-bad.xml"));
  check("broken XML -> NOT OK with 50005", bad.startsWith("NOT OK") && bad.includes("[50005]"));
  const wb = await upload("xlsx", join(fixtures, "EXAMPLE.XLSX"));
  check("workbook (.XLSX) -> OK: " + wb.split("\n")[0], wb.startsWith("OK"));

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
