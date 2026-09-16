// Real-browser test of web/index.html with Playwright (Chromium): serves web/ over HTTP, waits
// for the runtime, uploads a valid file, a broken file and a workbook, checks the reports.
//
//   cd .local/pyodide-test && npm install playwright@1.49.1
//   PLAYWRIGHT_BROWSERS_PATH=$PWD/browsers npx playwright install chromium
//   cd ../.. && python -m build && python tools/build_web.py && node tools/web_browser_test.mjs
//
// Needs network access for cdn.jsdelivr.net and pypi.org (the page loads Pyodide from there).

import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { writeFileSync, readFileSync, mkdirSync } from "node:fs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const scratch = process.env.PYODIDE_DIR || join(root, ".local", "pyodide-test");
process.env.PLAYWRIGHT_BROWSERS_PATH ||= join(scratch, "browsers");
const { chromium } = createRequire(join(scratch, "package.json"))("playwright");

// fixtures made with the installed package (any Python with aeoi importable works)
const fixtures = join(scratch, "fixtures");
mkdirSync(fixtures, { recursive: true });
const py = process.env.AEOI_PYTHON || join(root, ".venv", "Scripts", "python.exe");
await run(py, ["-c", `
from aeoi.crs import build, template
from aeoi.crs.example import sample_message
xml = build.build(sample_message(), "3.0", test=True).xml
open(r"${fixtures.replace(/\\/g, "\\\\")}/Test-report.xml", "w", encoding="utf-8").write(xml)
open(r"${fixtures.replace(/\\/g, "\\\\")}/Test-bad.xml", "w", encoding="utf-8").write(xml.replace("Beispiel AG", "Beispiel # AG"))
template.write_message(sample_message(), r"${fixtures.replace(/\\/g, "\\\\")}/example.xlsx")
`]);

const port = 8765;
const server = spawn(py, ["-m", "http.server", String(port), "--bind", "127.0.0.1", "--directory", join(root, "web")], { stdio: "ignore" });
await new Promise((r) => setTimeout(r, 1500));

let ok = true;
const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  const requests = [];
  page.on("request", (req) => requests.push(new URL(req.url()).host));
  await page.goto(`http://127.0.0.1:${port}/index.html`);
  await page.waitForFunction(() => document.getElementById("status").textContent.startsWith("Bereit"), null, { timeout: 240000 });
  console.log("runtime ready; version", await page.textContent("#ver"));

  async function upload(id, file) {
    await page.setInputFiles(`#${id}`, file);
    await page.waitForFunction(() => !document.getElementById("out").textContent.startsWith("Prüfung läuft"), null, { timeout: 120000 });
    return await page.textContent("#out");
  }
  const good = await upload("xml", join(fixtures, "Test-report.xml"));
  console.log("valid xml ->", good.split("\n")[0]);
  ok &&= good.startsWith("OK");
  const bad = await upload("xml", join(fixtures, "Test-bad.xml"));
  console.log("broken xml ->", bad.split("\n").slice(0, 2).join(" | "));
  ok &&= bad.startsWith("NOT OK") && bad.includes("[50005]");
  const wb = await upload("xlsx", join(fixtures, "example.xlsx"));
  console.log("workbook ->", wb.split("\n")[0]);
  ok &&= wb.startsWith("OK");

  const hosts = [...new Set(requests)].sort();
  console.log("hosts contacted:", hosts.join(", "));
  const allowed = new Set([`127.0.0.1:${port}`, "cdn.jsdelivr.net", "pypi.org", "files.pythonhosted.org"]);
  ok &&= hosts.every((h) => allowed.has(h));
} finally {
  await browser.close();
  server.kill();
}
console.log(ok ? "BROWSER TEST OK" : "BROWSER TEST FAILED");
process.exit(ok ? 0 : 1);

function run(cmd, args) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: "inherit" });
    p.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`${cmd} exited ${code}`))));
  });
}
