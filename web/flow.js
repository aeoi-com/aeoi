// Reporting flow on top of the validator: the registry file (the state; the browser is only a
// cache), build + encrypt from a checked workbook, record the portal's outcome. All Python calls
// go through aeoi.crs.workflow; this file only moves bytes and renders.
"use strict";

const REG_PATH = "/tmp/registry.sqlite";
const IDB_NAME = "aeoi";
// File System Access API (Chrome, Edge): the registry file is read and rewritten in place.
// Elsewhere, or with #nofsa in the URL (the automated test): open via <input type=file>, and
// every change downloads the new registry file.
const FSA = typeof window.showOpenFilePicker === "function" && !location.hash.includes("nofsa");

const reg = { open: false, name: "institut.sqlite", handle: null, view: null };

// ---------- Python side ----------
document.addEventListener("aeoi:booted", () => {
  py.runPython(`
import json, os
from aeoi.crs import template, workflow
from aeoi.messages import text as msg_text
from aeoi.registry import Registry, RegistryError
reg = None

def _error(exc, lang):
    """User-facing error in the page language; other exceptions keep their English text."""
    if isinstance(exc, (workflow.WorkflowError, RegistryError)) and exc.args:
        return json.dumps({"error": msg_text(exc.args[0], lang)})
    return json.dumps({"error": str(exc)})

def registry_open(fresh):
    global reg
    if reg is not None:
        reg.close()
    if fresh and os.path.exists("${REG_PATH}"):
        os.remove("${REG_PATH}")
    reg = Registry("${REG_PATH}")
    return json.dumps(workflow.registry_view(reg))

def registry_view():
    return json.dumps(workflow.registry_view(reg))

def registry_flush():
    """Close so the file bytes are complete, then reopen (the page reads the file in between)."""
    global reg
    if reg is not None:
        reg.close()
        reg = Registry("${REG_PATH}")

def remember_key(pem):
    return workflow.remember_public_key(reg, pem)

def plan_workbook(path, version, test, cancel, lang):
    report = check_workbook(path, version)
    if not report.ok or report.message is None:
        return json.dumps({"ok": False})
    keys = [k.strip() for k in cancel.split(",") if k.strip()]
    intent = workflow.plan(report.message, version, reg, test=test, cancel=keys)
    return json.dumps({"ok": True, **intent.as_dict(lang)})

def build_workbook(path, version, test, cancel, pem, lang, header):
    keys = [k.strip() for k in cancel.split(",") if k.strip()]
    try:
        _report, outs = workflow.build_from_workbook(path, version, reg, test=test, cancel=keys, public_key=pem or None, header=header)
    except (workflow.WorkflowError, RegistryError, ValueError) as exc:
        return _error(exc, lang)
    views = []
    for i, o in enumerate(outs):
        d = o.as_dict()
        d["xml_path"] = f"/tmp/out-{i}.xml"
        open(d["xml_path"], "w", encoding="utf-8").write(o.result.xml)
        if o.package is not None:
            d["package_path"] = f"/tmp/out-{i}.zip"
            open(d["package_path"], "wb").write(o.package)
        views.append(d)
    return json.dumps({"built": views})

def record(text, ref, lang):
    try:
        return json.dumps(workflow.record_outcome(reg, text, message_ref_id=ref or None, lang=lang))
    except (workflow.WorkflowError, RegistryError, ValueError) as exc:
        return _error(exc, lang)

def discard_message(ref):
    from aeoi.crs import submit
    submit.discard(reg, ref)
    return json.dumps(workflow.registry_view(reg))

def template_path(lang):
    template.write_template("/tmp/template.xlsx", lang=lang)
    return "/tmp/template.xlsx"

def restore_files(paths, workbook, status, lang):
    from pathlib import Path
    try:
        return json.dumps(workflow.restore_registry(reg, [Path(p) for p in json.loads(paths)], status=status, workbook=workbook or None, lang=lang))
    except (workflow.WorkflowError, RegistryError, ValueError) as exc:
        return _error(exc, lang)
`);
  for (const id of ["reg-open", "reg-new", "template-download"]) $(id).disabled = false;
  $("reg-note").textContent = t(FSA ? "reg_fsa_note" : "reg_fallback_note");
  restoreHandle();
});

// ---------- helpers ----------
function download(bytes, name, type) {
  const blob = new Blob([bytes], { type: type || "application/octet-stream" });
  const a = el("a", { href: URL.createObjectURL(blob), download: name });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}
function pyCall(name, ...args) {
  return py.globals.get(name)(...args);
}
function msg(node, text, ok) {
  node.textContent = text;
  node.className = "small " + (ok ? "msg-ok" : "msg-err");
}
const shortRef = (ref) => ref.length > 22 ? ref.slice(0, 12) + "…" + ref.slice(-6) : ref;

// ---------- registry: open / new / persist ----------
async function idb(mode, fn) {
  return new Promise((resolve, reject) => {
    const open = indexedDB.open(IDB_NAME, 1);
    open.onupgradeneeded = () => open.result.createObjectStore("handles");
    open.onerror = () => reject(open.error);
    open.onsuccess = () => {
      const tx = open.result.transaction("handles", mode);
      const req = fn(tx.objectStore("handles"));
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    };
  });
}
async function restoreHandle() {
  if (!FSA) return;
  try {
    const handle = await idb("readonly", (s) => s.get("registry"));
    if (!handle) return;
    const btn = $("reg-reopen");
    btn.textContent = t("reg_reopen_btn", { name: handle.name });
    btn.classList.remove("hidden");
    btn.onclick = async () => {
      if ((await handle.requestPermission({ mode: "readwrite" })) !== "granted") return;
      await openFromHandle(handle);
    };
    if ((await handle.queryPermission({ mode: "readwrite" })) === "granted") await openFromHandle(handle);
  } catch (e) { /* no IndexedDB: the user picks the file again */ }
}
async function openFromHandle(handle) {
  const file = await handle.getFile();
  await loadRegistryBytes(new Uint8Array(await file.arrayBuffer()), file.name, handle);
  try { await idb("readwrite", (s) => s.put(handle, "registry")); } catch (e) { /* ignore */ }
}
async function loadRegistryBytes(bytes, name, handle) {
  py.FS.writeFile(REG_PATH, bytes);
  reg.view = JSON.parse(pyCall("registry_open", false));
  reg.open = true; reg.name = name; reg.handle = handle || null;
  $("reg-reopen").classList.add("hidden");
  renderRegistry();
}
async function newRegistry() {
  let handle = null;
  if (FSA) {
    try {
      handle = await window.showSaveFilePicker({ suggestedName: "institut.sqlite", types: [{ description: "aeoi Register", accept: { "application/vnd.sqlite3": [".sqlite"] } }] });
    } catch (e) { return; } // cancelled
  }
  reg.view = JSON.parse(pyCall("registry_open", true));
  reg.open = true; reg.name = handle ? handle.name : "institut.sqlite"; reg.handle = handle;
  if (handle) try { await idb("readwrite", (s) => s.put(handle, "registry")); } catch (e) { /* ignore */ }
  renderRegistry();
  await persistRegistry();
}
async function openRegistry() {
  if (FSA) {
    let handle;
    try {
      [handle] = await window.showOpenFilePicker({ types: [{ description: "aeoi Register", accept: { "application/vnd.sqlite3": [".sqlite", ".db"] } }] });
    } catch (e) { return; }
    await openFromHandle(handle);
  } else {
    $("reg-file").click();
  }
}
$("reg-file").addEventListener("change", async (ev) => {
  const file = ev.target.files[0];
  if (!file) return;
  await loadRegistryBytes(new Uint8Array(await file.arrayBuffer()), file.name, null);
  ev.target.value = "";
});
async function persistRegistry() {
  // after every change: the file is the state
  pyCall("registry_flush");
  const bytes = py.FS.readFile(REG_PATH);
  if (reg.handle) {
    const w = await reg.handle.createWritable();
    await w.write(bytes); await w.close();
  } else {
    download(bytes, reg.name, "application/vnd.sqlite3");
  }
  reg.view = JSON.parse(pyCall("registry_view"));
  renderRegistry(new Date());
  console.info("aeoi:registry-saved " + bytes.length);
}
$("reg-open").addEventListener("click", openRegistry);
$("reg-new").addEventListener("click", newRegistry);
$("reg-download").addEventListener("click", () => { pyCall("registry_flush"); download(py.FS.readFile(REG_PATH), reg.name, "application/vnd.sqlite3"); });

function renderRegistry(savedAt) {
  const st = $("reg-status");
  if (!reg.open) { st.dataset.i18n = "reg_none"; st.textContent = t("reg_none"); st.classList.remove("ok"); return; }
  delete st.dataset.i18n;
  const v = reg.view;
  st.textContent = t("reg_opened", { name: reg.name, n: v.messages.length, pending: v.pending.length }) + (savedAt ? " · " + t("reg_saved", { time: savedAt.toLocaleTimeString(LOCALES[LANG]) }) : "");
  st.classList.add("ok");
  $("reg-download").classList.remove("hidden");
  const list = $("reg-list"); list.replaceChildren();
  if (v.messages.length) {
    const table = el("table");
    const head = el("tr");
    for (const k of ["reg_col_message", "reg_col_year", "reg_col_kind", "reg_col_records", "reg_col_status", "reg_col_created", ""]) head.append(el("th", { text: k ? t(k) : "" }));
    table.append(el("thead", {}, head));
    const body = el("tbody");
    for (const m of [...v.messages].reverse()) {
      const kind = (m.type === "CRS702" ? t("kind_correction") : m.type === "CRS703" ? t("kind_nil") : t("kind_new")) + (m.test ? " · " + t("kind_test") : "") + " · " + m.version;
      const actions = el("td");
      if (m.status === "built" || m.status === "submitted") {
        actions.append(
          el("button", { class: "btn", type: "button", text: t("reg_record_btn"), onclick: () => showOutcome(m.message_ref_id) }), " ",
          el("button", { class: "btn", type: "button", text: t("reg_discard_btn"), onclick: () => discardMessage(m.message_ref_id) }),
        );
      }
      body.append(el("tr", {},
        el("td", { class: "mono", text: shortRef(m.message_ref_id), title: m.message_ref_id }),
        el("td", { text: String(m.year) }), el("td", { text: kind }), el("td", { text: String(m.records) }),
        el("td", {}, el("span", { class: "status " + m.status, text: t("st_" + m.status) })),
        el("td", { text: (m.created_at || "").slice(0, 16).replace("T", " ") }), actions));
    }
    table.append(body); list.append(table);
  }
  fillOutcomeSelect();
  $("restore-card").classList.remove("hidden");
  $("outcome-card").classList.toggle("hidden", !v.pending.length);
  refreshKeyStatus();
  if (last && last.kind === "workbook" && last.data.ok) refreshPlan();
}
async function discardMessage(ref) {
  if (!confirm(t("reg_discard_confirm", { ref: shortRef(ref) }))) return;
  reg.view = JSON.parse(pyCall("discard_message", ref));
  await persistRegistry();
}

// ---------- restore a lost registry from the sent XML files ----------
$("restore-files").addEventListener("change", async (ev) => {
  const files = [...ev.target.files];
  ev.target.value = "";
  if (!files.length || !reg.open) return;
  const outNode = $("restore-out"); outNode.replaceChildren(); msg($("restore-msg"), t("working"), true);
  await nextPaint();
  try { py.FS.mkdir("/tmp/restore"); } catch (e) { /* exists */ }
  const paths = [];
  let workbook = last && last.kind === "workbook" && last.data.ok ? "/tmp/input.xlsx" : "";
  for (const file of files) {
    const bytes = new Uint8Array(await file.arrayBuffer());
    if (/\.xlsx$/i.test(file.name)) { workbook = "/tmp/restore/workbook.xlsx"; py.FS.writeFile(workbook, bytes); continue; }
    const path = "/tmp/restore/" + file.name.replace(/[^\w.-]+/g, "_");
    py.FS.writeFile(path, bytes); paths.push(path);
  }
  const res = JSON.parse(pyCall("restore_files", JSON.stringify(paths), workbook, $("restore-status").value, LANG));
  if (res.error) { msg($("restore-msg"), t("error_prefix") + res.error, false); console.info("aeoi:restored error"); return; }
  for (const f of res.restored) {
    const card = el("div", { class: "built" });
    const kind = (f.kind === "correction" ? t("kind_correction") : f.kind === "nil" ? t("kind_nil") : t("kind_new")) + (f.test ? " · " + t("kind_test") : "") + " · " + f.version + " · " + f.year;
    card.append(el("div", { class: "head" }, el("span", { text: f.name }), el("span", { class: "muted", text: kind + " · " + t("built_records", { n: f.records }) + " · " + t("st_" + f.status) })));
    card.append(el("div", { class: "ref", text: f.message_ref_id }));
    const keys = f.keys_from_workbook ? t("restore_keys_workbook", { n: f.keys_from_workbook }) : f.keys_from_number ? t("restore_keys_number", { n: f.keys_from_number }) : "";
    if (keys) card.append(el("div", { class: "small muted", text: keys }));
    for (const n of f.notes) card.append(el("div", { class: "small muted", text: n }));
    outNode.append(card);
  }
  for (const s of res.skipped) outNode.append(el("div", { class: "small msg-err", text: s.name + ": " + s.reason }));
  msg($("restore-msg"), t("restore_done", { n: res.restored.length, accounts: res.accounts }), true);
  if (res.restored.length) await persistRegistry();
  console.info("aeoi:restored " + res.restored.length + " " + res.skipped.length);
});

// ---------- template ----------
$("template-download").addEventListener("click", () => download(py.FS.readFile(pyCall("template_path", LANG)), `meldbar-vorlage-${LANG}.xlsx`, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"));

// ---------- build & encrypt ----------
let pendingKeyPem = null; // chosen this session but no registry to remember it in
document.addEventListener("aeoi:rendered", (ev) => {
  const r = ev.detail;
  const show = r && r.kind === "workbook" && r.data.ok;
  $("build-card").classList.toggle("hidden", !show);
  $("build-out").replaceChildren(); msg($("build-msg"), "", true);
  if (show) refreshPlan();
});
$("build-mode").addEventListener("change", refreshPlan);
$("version").addEventListener("change", () => { const v3 = $("version").value === "3.0"; $("header-row").classList.toggle("hidden", !v3); $("header-note").classList.toggle("hidden", !v3); });
let planTimer = null; // a plan of 3'000 accounts takes seconds: not on every keystroke
$("cancel-keys").addEventListener("input", () => { clearTimeout(planTimer); planTimer = setTimeout(refreshPlan, 400); });
let planSeq = 0;
async function refreshPlan() {
  const plan = $("plan");
  if (!last || last.kind !== "workbook") { plan.replaceChildren(); return; }
  const seq = ++planSeq;
  plan.replaceChildren(el("span", { class: "muted", text: t("working") }));
  $("build").disabled = true;
  await nextPaint();
  if (seq !== planSeq) return; // a newer request took over
  const test = $("build-mode").value === "test";
  const p = JSON.parse(pyCall("plan_workbook", "/tmp/input.xlsx", $("version").value, test, $("cancel-keys").value, LANG));
  plan.replaceChildren();
  if (!p.ok) return;
  const tags = [["new", p.new.length, "plan_new"], ["changed", p.changed.length, "plan_changed"], ["unchanged", p.unchanged.length, "plan_unchanged"], ["deleted", p.deletions.length, "plan_deleted"], ["blocked", p.blocked.length, "plan_blocked"]];
  for (const [cls, n, key] of tags) if (n) plan.append(el("span", { class: "tag " + cls, text: t(key, { n }) }));
  if (p.nil) plan.append(el("span", { class: "tag", text: t("plan_nil") }));
  let sum = "";
  if (p.blocked.length) sum = p.problems.every((x) => x.includes("(80002)") && /not accepted|nicht angenommen/.test(x)) ? t("plan_pending") : p.problems.join(" · ");
  else if (!test && !reg.open) sum = t("build_need_registry");
  else if (p.messages.length === 2) sum = t("plan_messages_both");
  else if (p.messages[0] === "correction") sum = t("plan_messages_correction");
  else if (p.messages[0] === "new") sum = t("plan_messages_new");
  else sum = t("plan_nothing");
  plan.append(el("div", { class: "sum" + (p.blocked.length ? " msg-err" : ""), text: sum }));
  $("build").disabled = !!p.blocked.length || (!test && !reg.open) || !p.messages.length;
}
function refreshKeyStatus() {
  const has = (reg.open && reg.view && reg.view.has_key) || !!pendingKeyPem;
  const ks = $("key-status");
  ks.textContent = has ? t("key_remembered") : t("key_none");
  ks.className = has ? "msg-ok" : "";
}
$("key-file").addEventListener("change", async (ev) => {
  const file = ev.target.files[0];
  if (!file) return;
  const bytes = new Uint8Array(await file.arrayBuffer()); // PEM or DER, key or certificate
  ev.target.value = "";
  try {
    py.globals.set("_key_bytes", bytes);
    const pem = py.runPython("from aeoi.estv import packaging; packaging.public_key_pem(packaging.load_public_key(bytes(_key_bytes.to_py())))");
    if (reg.open) { pyCall("remember_key", pem); await persistRegistry(); }
    else pendingKeyPem = pem;
    refreshKeyStatus();
  } catch (e) {
    msg($("build-msg"), t("key_bad") + e, false);
  }
});
$("build").addEventListener("click", async () => {
  const test = $("build-mode").value === "test";
  const outNode = $("build-out"); outNode.replaceChildren();
  msg($("build-msg"), t("working"), true);
  $("build").disabled = true;
  await nextPaint();
  try {
    const header = $("version").value === "3.0" ? $("build-header").value : "oecd";
    const res = JSON.parse(pyCall("build_workbook", "/tmp/input.xlsx", $("version").value, test, $("cancel-keys").value, pendingKeyPem || "", LANG, header));
    if (res.error) { msg($("build-msg"), t("error_prefix") + res.error, false); console.info("aeoi:built error"); return; }
    const views = res.built;
    for (const v of views) {
      const card = el("div", { class: "built" });
      card.append(el("div", { class: "head" }, el("span", { text: (v.kind === "correction" ? t("kind_correction") : t("kind_new")) + (test ? " · " + t("kind_test") : "") }), el("span", { class: "muted", text: t("built_records", { n: v.records }) + (v.header === "wegleitung" ? " · " + t("built_header_wegleitung") : "") })));
      card.append(el("div", { class: "ref", text: v.message_ref_id }));
      const actions = el("div", { class: "actions" });
      if (v.encrypted) actions.append(el("button", { class: "btn primary", type: "button", text: t("dl_package") + " · " + v.package_name, onclick: () => download(py.FS.readFile(v.package_path), v.package_name, "application/zip") }));
      else actions.append(el("span", { class: "muted small", text: t("built_unencrypted") }));
      actions.append(el("button", { class: "btn", type: "button", text: t("dl_xml") + " · " + v.xml_name, onclick: () => download(py.FS.readFile(v.xml_path), v.xml_name, "application/xml") }));
      card.append(actions);
      outNode.append(card);
    }
    outNode.append(el("div", { class: "next" }, el("strong", { text: t("next_steps_title") + ": " }), t("next_steps")));
    msg($("build-msg"), t("build_done", { n: views.length }), true);
    if (reg.open) await persistRegistry();
    console.info("aeoi:built " + views.map((v) => v.kind + ":" + v.message_ref_id).join(" "));
  } catch (e) {
    const text = String(e).split("\n").filter((l) => l.includes("Error")).pop() || String(e);
    msg($("build-msg"), t("error_prefix") + text.replace(/^.*?Error: /, ""), false);
    console.info("aeoi:built error");
  } finally {
    $("build").disabled = false;
  }
});

// ---------- outcome ----------
function fillOutcomeSelect() {
  const sel = $("outcome-ref"); sel.replaceChildren();
  if (!reg.open) return;
  for (const ref of reg.view.pending) sel.append(el("option", { value: ref, text: shortRef(ref) }));
}
function showOutcome(ref) {
  $("outcome-card").classList.remove("hidden");
  $("outcome-ref").value = ref;
  $("outcome-card").scrollIntoView({ behavior: "smooth", block: "start" });
  $("outcome-text").focus();
}
$("outcome-file").addEventListener("change", async (ev) => {
  const file = ev.target.files[0];
  if (!file) return;
  $("outcome-text").value = await file.text();
  ev.target.value = "";
});
$("outcome-record").addEventListener("click", async () => {
  const out = $("outcome-out"); out.replaceChildren();
  msg($("outcome-msg"), t("working"), true);
  await nextPaint();
  try {
    const v = JSON.parse(pyCall("record", $("outcome-text").value, $("outcome-ref").value, LANG));
    if (v.error) { msg($("outcome-msg"), t("error_prefix") + v.error, false); console.info("aeoi:outcome error"); return; }
    msg($("outcome-msg"), v.status === "submitted" ? t("outcome_portal_error") : v.accepted ? t("outcome_accepted", { ref: shortRef(v.message_ref_id) }) : t("outcome_rejected"), !!v.accepted);
    for (const f of v.findings) {
      const card = el("article", { class: "finding error" }, el("div", { class: "head" }, el("span", { class: "code", text: f.code }), el("span", { class: "title", text: f.title })));
      if (f.doc_ref_ids.length) { const loc = el("div", { class: "loc" }); for (const d of f.doc_ref_ids) loc.append(el("span", { class: "path", text: d })); card.append(loc); }
      card.append(el("div", { class: "fix" }, svg(ICON_FIX), el("span", {}, el("strong", { text: t("fix_label") + ": " }), f.fix)));
      if (f.details) card.append(el("div", { class: "msg mono", text: f.details }));
      if (f.should_have_been_caught) card.append(el("div", { class: "msg msg-err", text: t("outcome_bug") }));
      out.append(card);
    }
    $("outcome-text").value = "";
    await persistRegistry();
    console.info("aeoi:outcome " + v.status);
  } catch (e) {
    const text = String(e).split("\n").filter((l) => l.includes("Error")).pop() || String(e);
    msg($("outcome-msg"), t("error_prefix") + text.replace(/^.*?Error: /, ""), false);
    console.info("aeoi:outcome error");
  }
});

document.addEventListener("aeoi:language", () => {
  $("reg-note").textContent = t(FSA ? "reg_fsa_note" : "reg_fallback_note");
  if (reg.open) renderRegistry();
});
