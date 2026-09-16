// Headless smoke test of the browser validator: runs the same Python as web/index.html inside
// Pyodide under Node, against the built wheel. Setup (once, outside the repo tree):
//
//   mkdir -p .local/pyodide-test && cd .local/pyodide-test && npm install pyodide@0.27.7
//   cd ../.. && python -m build && node tools/web_smoke.mjs
//
// The pyodide package is resolved from .local/pyodide-test/node_modules (or $PYODIDE_DIR).

import { readFileSync, readdirSync } from "node:fs";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const pyodideDir = process.env.PYODIDE_DIR || join(root, ".local", "pyodide-test");
const { loadPyodide } = createRequire(join(pyodideDir, "package.json"))("pyodide");

const wheelName = readdirSync(join(root, "dist")).find((f) => f.endsWith(".whl"));
if (!wheelName) throw new Error("no wheel in dist/: run python -m build first");
const wheel = readFileSync(join(root, "dist", wheelName));

const py = await loadPyodide();
await py.loadPackage(["lxml", "pydantic", "micropip", "cryptography"]);
const micropip = py.pyimport("micropip");
await micropip.install(["xmlschema", "xsdata==24.12", "openpyxl"]);
py.FS.writeFile("/tmp/" + wheelName, wheel);
await micropip.install("emfs:/tmp/" + wheelName);

const report = py.runPython(`
import time
from aeoi.crs import build, flat, model, template, validate
from aeoi.crs.example import sample_message
out = []
t0 = time.time()
xml = build.build(sample_message(), "3.0", test=True).xml
open("/tmp/Test-report.xml", "w", encoding="utf-8").write(xml)
rep = validate.validate_file("/tmp/Test-report.xml")
out.append(f"validate 3.0: {'OK' if rep.ok else 'NOT OK'} ({time.time()-t0:.1f}s)")
bad = xml.replace("Beispiel AG", "Beispiel # AG")
open("/tmp/Test-bad.xml", "w", encoding="utf-8").write(bad)
rep = validate.validate_file("/tmp/Test-bad.xml")
out.append(f"validate bad: {[p.rule for p in rep.problems]}")
t0 = time.time()
template.write_message(sample_message(), "/tmp/example.xlsx")
r = flat.read("/tmp/example.xlsx")
errors = [p for p in model.check_message(r.message, "3.0").problems if p.rule != "info"]
out.append(f"workbook: {len(r.problems)} input problems, {len(errors)} errors ({time.time()-t0:.1f}s)")
"\\n".join(out)
`);
console.log(report);
const ok = report.includes("validate 3.0: OK") && report.includes("['50005']") && report.includes("0 input problems, 0 errors");
console.log(ok ? "WEB SMOKE OK" : "WEB SMOKE FAILED");
process.exit(ok ? 0 : 1);
