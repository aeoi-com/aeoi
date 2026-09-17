// aeoi browser validator. Runs the Python package in Pyodide; files are read into the in-memory
// file system of the page and never sent anywhere (see the CSP in index.html).
"use strict";

const WHEEL = "aeoi-0.0.1-py3-none-any.whl";
const PYODIDE_PACKAGES = ["lxml", "pydantic", "micropip", "cryptography"];
const PYPI_PACKAGES = ["xmlschema", "xsdata==24.12", "openpyxl"]; // xsdata 26 needs typing-extensions>=4.12, Pyodide ships 4.11

const status = document.getElementById("status");
const out = document.getElementById("out");
let py = null;

async function boot() {
  try {
    py = await loadPyodide();
    status.textContent = "Bibliotheken werden geladen …";
    await py.loadPackage(PYODIDE_PACKAGES);
    const micropip = py.pyimport("micropip");
    await micropip.install(PYPI_PACKAGES);
    await micropip.install(new URL(WHEEL, location.href).href);
    document.getElementById("ver").textContent = py.runPython("import aeoi; aeoi.__version__");
    status.textContent = "Bereit. Ab jetzt findet keine Netzanfrage mehr statt.";
    status.className = "ok";
    document.getElementById("xml").disabled = false;
    document.getElementById("xlsx").disabled = false;
  } catch (e) {
    status.textContent = "Die Laufzeit konnte nicht geladen werden: " + e;
    status.className = "err";
  }
}

function writeFixed(name, bytes) {
  // fixed in-memory path; the original name is passed separately (Test… rule for XML files)
  py.FS.writeFile(name, bytes);
  return name;
}

async function validateXml(file) {
  const bytes = new Uint8Array(await file.arrayBuffer());
  const path = writeFixed("/tmp/input.xml", bytes);
  const mode = document.getElementById("mode").value;
  py.globals.set("path", path);
  py.globals.set("original_name", file.name);
  py.globals.set("mode", mode);
  return py.runPython(`
from aeoi.crs import validate
test = None if mode == "auto" else (mode == "test")
if test is None:
    test = original_name.lower().startswith("test")
validate.validate_file(path, test=test).render()
`);
}

async function checkWorkbook(file) {
  const bytes = new Uint8Array(await file.arrayBuffer());
  const path = writeFixed("/tmp/input.xlsx", bytes);
  py.globals.set("path", path);
  py.globals.set("version", document.getElementById("version").value);
  return py.runPython(`
from aeoi.crs.check import check_workbook
check_workbook(path, version).render()
`);
}

for (const [id, fn] of [["xml", validateXml], ["xlsx", checkWorkbook]]) {
  document.getElementById(id).addEventListener("change", async (ev) => {
    const file = ev.target.files[0];
    if (!file) return;
    out.textContent = "Prüfung läuft …";
    out.className = "";
    try {
      const text = await fn(file);
      out.textContent = text;
      out.className = text.startsWith("OK") ? "ok" : "err";
    } catch (e) {
      out.textContent = "Fehler bei der Prüfung: " + e;
      out.className = "err";
    }
    ev.target.value = "";
  });
}
boot();
