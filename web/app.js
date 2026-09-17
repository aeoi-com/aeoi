// aeoi browser validator. Runs the Python package in Pyodide; files are read into the in-memory
// file system of the page and never sent anywhere (see the CSP in index.html).
"use strict";

const WHEEL = "aeoi-0.0.1-py3-none-any.whl";
const PYODIDE_PACKAGES = ["lxml", "pydantic", "micropip", "cryptography", "sqlite3"]; // sqlite3: the registry
const WHEELS = ["wheels/xmlschema-4.3.2-py3-none-any.whl", "wheels/elementpath-5.1.4-py3-none-any.whl", "wheels/xsdata-24.12-py3-none-any.whl", "wheels/openpyxl-3.1.5-py2.py3-none-any.whl", "wheels/et_xmlfile-2.0.0-py3-none-any.whl"]; // vendored pure-Python wheels, filled in by tools/build_web.py (installed with deps=False)
const LOCALES = { de: "de-CH", fr: "fr-CH", it: "it-CH" };

const $ = (id) => document.getElementById(id);
applyLanguage(initialLanguage()); // every dictionary file is loaded now
const status = $("status");
const out = $("out");
let py = null;
let last = null; // { name, kind, ms, data } of the last check; the report object stays in Python

// ---------- small DOM helpers (no innerHTML for anything that carries file content) ----------
function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of children) if (c != null) node.append(c);
  return node;
}
function svg(path, extra) {
  const s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  s.setAttribute("viewBox", "0 0 24 24"); s.setAttribute("fill", "none"); s.setAttribute("stroke", "currentColor");
  s.setAttribute("stroke-width", "2.4"); s.setAttribute("stroke-linecap", "round"); s.setAttribute("stroke-linejoin", "round");
  const p = document.createElementNS("http://www.w3.org/2000/svg", "path"); p.setAttribute("d", path); s.append(p);
  if (extra) s.setAttribute("class", extra);
  return s;
}
const ICON_OK = "M5 12.5l4.5 4.5L19 7";
const ICON_BAD = "M6 6l12 12M18 6L6 18";
const ICON_FIX = "M12 3v3M12 18v3M3 12h3M18 12h3M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z";
const fmtNum = (n) => new Intl.NumberFormat(LOCALES[LANG] || "de-CH").format(n);
const fmtMs = (ms) => (ms < 1000 ? `${Math.round(ms)} ms` : `${(ms / 1000).toFixed(1)} s`);
function regionName(code) {
  try { return new Intl.DisplayNames([LOCALES[LANG] || "de-CH"], { type: "region" }).of(code) || code; } catch (e) { return code; }
}

// ---------- theme ----------
function applyTheme(mode, store) {
  if (mode === "auto") document.documentElement.removeAttribute("data-theme");
  else document.documentElement.setAttribute("data-theme", mode);
  const dark = mode === "dark" || (mode === "auto" && matchMedia("(prefers-color-scheme: dark)").matches);
  $("theme-sun").classList.toggle("hidden", dark);
  $("theme-moon").classList.toggle("hidden", !dark);
  $("theme").dataset.mode = mode;
  $("theme").setAttribute("aria-label", t("theme", { mode: t("theme_" + mode) }));
  if (store) try { localStorage.setItem("aeoi-theme", mode); } catch (e) { /* ignore */ }
}
(function initTheme() {
  let mode = "auto";
  try { mode = localStorage.getItem("aeoi-theme") || "auto"; } catch (e) { /* ignore */ }
  applyTheme(mode, false);
  $("theme").addEventListener("click", () => {
    const next = { auto: "light", light: "dark", dark: "auto" }[$("theme").dataset.mode] || "auto";
    applyTheme(next, true);
  });
})();

// ---------- boot ----------
function setStatus(key, extra) {
  status.dataset.i18n = key; // the key is kept so a language switch re-renders the text
  status.textContent = t(key) + (extra || "");
}
function step(n) {
  for (const s of document.querySelectorAll("#steps .step")) {
    const k = Number(s.dataset.step);
    s.classList.toggle("done", k < n);
    s.classList.toggle("active", k === n);
  }
}
async function boot() {
  const t0 = performance.now();
  try {
    step(1);
    py = await loadPyodide({ indexURL: new URL("pyodide/", location.href).href }); // same origin, nothing else
    step(2); setStatus("libs");
    await py.loadPackage(PYODIDE_PACKAGES);
    const micropip = py.pyimport("micropip");
    await micropip.install(WHEELS.map((w) => new URL(w, location.href).href), { deps: false });
    step(3); setStatus("rules");
    await micropip.install(new URL(WHEEL, location.href).href, { deps: false });
    py.runPython(`
import json, re
import aeoi
from aeoi.crs import build, overview, template, validate
from aeoi.crs.check import check_workbook
from aeoi.crs.example import sample_message
last_report = None

def run_xml(path, test, lang):
    global last_report
    last_report = validate.validate_file(path, test=test)
    return json.dumps(overview.report_dict(last_report, lang))

def run_workbook(path, version, lang):
    global last_report
    last_report = check_workbook(path, version)
    return json.dumps(overview.report_dict(last_report, lang))

def rerender(lang):
    return json.dumps(overview.report_dict(last_report, lang)) if last_report is not None else None

def sample_xml(broken):
    xml = build.build(sample_message(), "3.0", test=True).xml
    if broken:
        xml = xml.replace("Beispiel AG", "Beispiel # AG")
        xml = re.sub(r"(<crs:AccountNumber[^>]*>CH)(\\d\\d)", lambda m: m.group(1) + ("00" if m.group(2) != "00" else "01"), xml, count=1)
        xml = re.sub(r"<crs:BirthDate>\\d{4}", "<crs:BirthDate>2031", xml, count=1)
        xml = re.sub(r"<crs:AccountBalance([^>]*)>[\\d.]+", r"<crs:AccountBalance\\1>-100.00", xml, count=1)
    return xml

def sample_xlsx():
    template.write_message(sample_message(), "/tmp/sample.xlsx")
    return "/tmp/sample.xlsx"
`);
    step(5);
    $("bar").classList.add("done");
    $("ver").textContent = py.runPython("aeoi.__version__");
    setStatus("ready");
    status.className = "ok";
    unlock();
    document.dispatchEvent(new CustomEvent("aeoi:booted"));
    console.info("aeoi:ready", Math.round(performance.now() - t0) + "ms");
  } catch (e) {
    setStatus("boot_error", String(e));
    status.className = "err";
    console.error(e);
  }
}
function unlock() {
  const drop = $("drop");
  drop.classList.remove("locked");
  drop.classList.add("unlocked");
  $("file").disabled = false;
  for (const id of ["sample-ok", "sample-bad", "sample-xlsx"]) $(id).disabled = false;
}

// ---------- checking ----------
function kindOf(name) {
  return /\.xlsx$/i.test(name) ? "workbook" : "xml";
}
async function checkFile(name, bytes) {
  if (!py) return;
  $("busy").classList.remove("hidden");
  $("results").classList.add("hidden");
  const t0 = performance.now();
  try {
    const kind = kindOf(name);
    const path = kind === "workbook" ? "/tmp/input.xlsx" : "/tmp/input.xml"; // fixed in-memory path; the name is only used for the Test rule
    py.FS.writeFile(path, bytes);
    let json;
    if (kind === "workbook") {
      json = py.globals.get("run_workbook")(path, $("version").value, LANG);
    } else {
      const mode = $("mode").value;
      const test = mode === "auto" ? name.toLowerCase().startsWith("test") : mode === "test";
      json = py.globals.get("run_xml")(path, test, LANG);
    }
    const ms = performance.now() - t0;
    last = { name, kind, ms, data: JSON.parse(json) };
    render();
  } catch (e) {
    last = null;
    out.textContent = t("check_error") + e;
    $("results").classList.remove("hidden");
    renderError(String(e));
    console.error(e);
  } finally {
    $("busy").classList.add("hidden");
    console.info("aeoi:result " + out.textContent.split("\n")[0]);
  }
}

$("file").addEventListener("change", async (ev) => {
  const file = ev.target.files[0];
  if (!file) return;
  const bytes = new Uint8Array(await file.arrayBuffer());
  ev.target.value = "";
  await checkFile(file.name, bytes);
});
(function dragDrop() {
  const drop = $("drop");
  for (const evn of ["dragenter", "dragover"]) drop.addEventListener(evn, (e) => { e.preventDefault(); if (py) drop.classList.add("over"); });
  for (const evn of ["dragleave", "drop"]) drop.addEventListener(evn, (e) => { e.preventDefault(); drop.classList.remove("over"); });
  drop.addEventListener("drop", async (e) => {
    const file = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
    if (!file || !py) return;
    await checkFile(file.name, new Uint8Array(await file.arrayBuffer()));
  });
})();
$("sample-ok").addEventListener("click", () => checkFile("Test-Beispiel.xml", new TextEncoder().encode(py.globals.get("sample_xml")(false))));
$("sample-bad").addEventListener("click", () => checkFile("Test-Beispiel-Fehler.xml", new TextEncoder().encode(py.globals.get("sample_xml")(true))));
$("sample-xlsx").addEventListener("click", () => { const p = py.globals.get("sample_xlsx")(); checkFile("Beispiel-Vorlage.xlsx", py.FS.readFile(p)); });
$("again").addEventListener("click", () => { $("results").classList.add("hidden"); $("input").scrollIntoView({ behavior: "smooth", block: "start" }); });
$("download").addEventListener("click", () => {
  if (!last) return;
  const blob = new Blob([out.textContent], { type: "text/plain;charset=utf-8" });
  const a = el("a", { href: URL.createObjectURL(blob), download: `${t("report_name")}-${last.name.replace(/\.[^.]+$/, "")}.txt` });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
});
$("copy").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText(out.textContent); } catch (e) { return; }
  const label = $("copy").querySelector("span");
  label.textContent = t("copied");
  setTimeout(() => { label.textContent = t("copy"); }, 1500);
});
document.addEventListener("aeoi:language", () => {
  applyTheme($("theme").dataset.mode || "auto", false);
  if (!last || !py) return;
  const json = py.globals.get("rerender")(LANG);
  if (json) { last.data = JSON.parse(json); render(false); }
});

// ---------- rendering ----------
function render(scroll = true) {
  const { data, name, kind, ms } = last;
  const results = $("results");
  results.classList.remove("hidden");
  out.textContent = data.text;

  // verdict
  const v = $("verdict");
  v.classList.toggle("ok", data.ok);
  v.classList.toggle("bad", !data.ok);
  $("sigil").replaceChildren(svg(data.ok ? ICON_OK : ICON_BAD));
  const unreadable = kind === "workbook" && data.overview === null;
  $("verdict-title").textContent = data.ok ? t("verdict_ok") : unreadable ? t("verdict_unreadable") : t("verdict_bad");
  $("verdict-sub").textContent = t(kind === "workbook" ? "sub_workbook" : "sub_xml", { version: data.version || "?", time: fmtMs(ms) });
  $("verdict-file").textContent = name;

  // stats
  const stats = $("stats"); stats.replaceChildren();
  const ov = data.overview;
  const cells = [
    ["err", data.counts.error, t("stat_errors")],
    kind === "workbook" ? ["err", data.counts.input, t("stat_inputs")] : null,
    ["info", data.counts.info, t("stat_notes")],
    ov ? ["", ov.accounts, t("stat_accounts")] : null,
    ov ? ["", ov.individuals, t("stat_persons")] : null,
    ov ? ["", ov.organisations, t("stat_entities")] : null,
    ov ? ["", ov.controlling_persons, t("stat_cp")] : null,
  ].filter(Boolean);
  for (const [cls, n, k] of cells) {
    const val = el("div", { class: "v", text: "0" });
    stats.append(el("div", { class: "stat " + (n === 0 && cls === "err" ? "ok" : cls) }, val, el("div", { class: "k", text: k })));
    countUp(val, n);
  }

  // overview
  $("overview").classList.toggle("hidden", !ov);
  if (ov) renderOverview(ov);

  // findings
  renderFindings(data);
  document.dispatchEvent(new CustomEvent("aeoi:rendered", { detail: last }));
  if (scroll) results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderError(message) {
  document.dispatchEvent(new CustomEvent("aeoi:rendered", { detail: null }));
  $("verdict").classList.remove("ok"); $("verdict").classList.add("bad");
  $("sigil").replaceChildren(svg(ICON_BAD));
  $("verdict-title").textContent = t("verdict_unreadable");
  $("verdict-sub").textContent = message;
  $("verdict-file").textContent = "";
  $("stats").replaceChildren();
  $("overview").classList.add("hidden");
  $("filters").replaceChildren(); $("findings").replaceChildren();
  $("no-findings").classList.add("hidden");
}

function countUp(node, target) {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches || target <= 1) { node.textContent = fmtNum(target); return; }
  const start = performance.now(), dur = 600;
  const tick = (now) => {
    const p = Math.min(1, (now - start) / dur);
    node.textContent = fmtNum(Math.round(target * (1 - Math.pow(1 - p, 3))));
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

function renderOverview(ov) {
  const kv = $("ov-kv"); kv.replaceChildren();
  const flags = [];
  if (ov.closed) flags.push(t("flag_closed", { n: ov.closed }));
  if (ov.undocumented) flags.push(t("flag_undocumented", { n: ov.undocumented }));
  if (ov.dormant) flags.push(t("flag_dormant", { n: ov.dormant }));
  if (ov.joint) flags.push(t("flag_joint", { n: ov.joint }));
  const balances = Object.entries(ov.balances).map(([c, v]) => `${fmtNum(Number(v))} ${c}`).join(" · ");
  const rows = [
    [t("kv_fi"), ov.fi_name],
    [t("kv_id"), ov.estv_id],
    [t("kv_year"), String(ov.year)],
    [t("kv_type"), t("type_" + ov.message_type_indic)],
    [t("kv_balances"), balances || "-"],
    [t("kv_flags"), flags.length ? flags.join(", ") : t("flag_none")],
  ];
  for (const [k, v] of rows) kv.append(el("dt", { text: k }), el("dd", { text: v }));

  // ring: holder types
  const ring = $("ov-ring"); ring.replaceChildren();
  const parts = [
    ["individual", ov.holder_types.individual || 0, "var(--accent)"],
    ["CRS101", ov.holder_types.CRS101 || 0, "var(--accent-2)"],
    ["CRS102", ov.holder_types.CRS102 || 0, "var(--info)"],
    ["CRS103", ov.holder_types.CRS103 || 0, "var(--warn)"],
  ].filter((p) => p[1] > 0);
  const total = parts.reduce((a, p) => a + p[1], 0);
  if (total) {
    const NS = "http://www.w3.org/2000/svg";
    const s = document.createElementNS(NS, "svg"); s.setAttribute("viewBox", "0 0 100 100");
    const r = 40, C = 2 * Math.PI * r;
    const track = document.createElementNS(NS, "circle");
    for (const [k, v] of [["cx", 50], ["cy", 50], ["r", r]]) track.setAttribute(k, v);
    track.setAttribute("class", "track"); s.append(track);
    let offset = 0;
    const segs = [];
    for (const [, n, color] of parts) {
      const c = document.createElementNS(NS, "circle");
      for (const [k, v] of [["cx", 50], ["cy", 50], ["r", r]]) c.setAttribute(k, v);
      c.setAttribute("class", "seg"); c.setAttribute("stroke", color);
      c.setAttribute("stroke-dasharray", `0 ${C}`); c.setAttribute("stroke-dashoffset", String(-offset));
      s.append(c); segs.push([c, (n / total) * C]);
      offset += (n / total) * C;
    }
    const legend = el("div", { class: "legend" });
    for (const [key, n, color] of parts) {
      const i = el("i"); i.style.background = color;
      legend.append(el("div", {}, i, el("span", { text: t("leg_" + key) }), el("span", { class: "n", text: fmtNum(n) })));
    }
    ring.append(s, legend);
    requestAnimationFrame(() => { for (const [c, len] of segs) c.setAttribute("stroke-dasharray", `${len} ${C - len}`); });
  }

  // bars: residence countries
  const bars = $("ov-bars"); bars.replaceChildren();
  const top = ov.residence.slice(0, 8);
  const max = Math.max(1, ...top.map((x) => x.count));
  const fills = [];
  for (const { code, count } of top) {
    const fill = el("div", { class: "fill" });
    const lbl = el("div", { class: "lbl" }, el("b", { text: code }), regionName(code));
    bars.append(el("div", { class: "row" }, lbl, el("div", { class: "track" }, fill), el("div", { class: "n", text: fmtNum(count) })));
    fills.push([fill, (count / max) * 100]);
  }
  if (!top.length) bars.append(el("div", { class: "small muted", text: t("ov_none") }));
  requestAnimationFrame(() => { for (const [f, w] of fills) f.style.width = w + "%"; });
}

let filter = "all";
function renderFindings(data) {
  const filters = $("filters"); filters.replaceChildren();
  const counts = data.counts;
  const chips = [["all", data.problems.length], ["error", counts.error], ["input", counts.input], ["info", counts.info]].filter(([k, n]) => k === "all" || n > 0);
  if (!chips.some(([k]) => k === filter)) filter = "all";
  for (const [k, n] of chips) {
    const chip = el("button", { class: "chip", type: "button", "aria-pressed": String(filter === k), onclick: () => { filter = k; renderFindings(data); } },
      t("f_" + k), el("span", { class: "cnt", text: fmtNum(n) }));
    filters.append(chip);
  }
  const list = $("findings"); list.replaceChildren();
  const shown = data.problems.filter((p) => filter === "all" || p.severity === filter);
  $("no-findings").classList.toggle("hidden", data.problems.length > 0);
  filters.classList.toggle("hidden", data.problems.length === 0);
  for (const p of shown) list.append(finding(p));
}

function locationChips(p) {
  const chips = [];
  if (p.scope === "account") chips.push(t("loc_account", { ref: p.ref }));
  else if (p.scope === "fi") chips.push(t("loc_fi"));
  else if (p.scope === "header") chips.push(t("loc_header"));
  else if (p.scope === "workbook") { if (p.sheet) chips.push(t("loc_sheet", { sheet: p.sheet })); if (p.row != null) chips.push(t("loc_row", { row: p.row })); }
  else chips.push(t("loc_file"));
  if (p.controlling_person != null) chips.push(t("loc_cp", { n: p.controlling_person + 1 }));
  return chips;
}

function finding(p) {
  const card = el("article", { class: "finding " + p.severity });
  const head = el("div", { class: "head" }, el("span", { class: "code", text: p.rule || "aeoi" }), el("span", { class: "title", text: p.title }));
  const loc = el("div", { class: "loc" });
  for (const c of locationChips(p)) loc.append(el("span", { text: c }));
  if (p.field) loc.append(el("span", { class: "path", text: p.field }));
  card.append(head, loc);
  if (p.severity === "info") {
    card.append(el("div", { class: "msg", text: p.message }));
    return card;
  }
  card.append(el("div", { class: "fix" }, svg(ICON_FIX), el("span", {}, el("strong", { text: t("fix_label") + ": " }), p.fix)));
  const details = el("details", {}, el("summary", { text: t("technical_label") + (p.official ? " · " + t("official_label") : "") }),
    el("div", { class: "msg mono", text: `${p.where}: ${p.message}` }));
  if (p.official) details.append(el("blockquote", { text: p.official }));
  card.append(details);
  return card;
}

boot();

// Offline after the first visit: the service worker precaches every file of the app. Only on a
// secure context (https or localhost); it never contacts another host.
if ("serviceWorker" in navigator && (location.protocol === "https:" || ["localhost", "127.0.0.1"].includes(location.hostname))) {
  navigator.serviceWorker.register("sw.js").then((r) => {
    navigator.serviceWorker.ready.then(() => console.info("aeoi:sw ready"));
    r.addEventListener("updatefound", () => console.info("aeoi:sw update"));
  }).catch((e) => console.warn("service worker not registered:", e));
}
