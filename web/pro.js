// Loader for the meldbar Pro pack. This file is part of the open page (Apache-2.0); the pack
// itself is proprietary and reaches the browser only as an encrypted bundle that lives on the
// page's own origin (pro/<id>.bin). Everything is derived from the licence key in the browser
// (WebCrypto): the bundle's file name (HMAC-SHA256) and the AES-256-GCM key (HKDF-SHA256). No
// server, no request to any other host; an unknown key just names a file that does not exist.
// The licence key is kept in localStorage of this browser only. The blob is cached (Cache API)
// so an activated licence keeps working offline.
"use strict";

Object.assign(I18N.de, {
  pro_title: "meldbar Pro",
  pro_intro: "Mit einer Pro-Lizenz erstellt die App zu jeder Prüfung und zu jeder erstellten Meldung ein Prüfprotokoll als PDF: Datei-Hash, Meldung, Ergebnis, Befunde, jede geprüfte Regel, Kennungen und Hashes der gesendeten Datei - für das Dossier des Vehikels. Der Lizenzschlüssel wird nur in diesem Browser gespeichert; das Pro-Paket wird verschlüsselt von dieser Seite geladen und hier entschlüsselt.",
  pro_key_label: "Lizenzschlüssel",
  pro_activate: "Aktivieren",
  pro_remove: "Lizenz entfernen",
  pro_working: "Pro-Paket wird geladen …",
  pro_active: "Pro aktiv für {holder} · gültig bis {until} · {n} Vehikel",
  pro_grace: "Pro-Lizenz für {holder} ist am {until} abgelaufen - noch {days} Tage nutzbar. Bitte verlängern.",
  pro_expired: "Pro-Lizenz für {holder} ist am {until} abgelaufen.",
  pro_bad_key: "Kein gültiger Schlüssel (Form: MB1-XXXXX-XXXXX-XXXXX-XXXXX).",
  pro_unknown: "Dieser Schlüssel ist auf dieser Seite nicht bekannt. Tippfehler? Neue Lizenzen sind nach der nächsten Veröffentlichung der Seite aktiv.",
  pro_offline: "Das Pro-Paket ist nicht im Cache und die Seite ist offline. Einmal online aktivieren.",
  pro_failed: "Das Pro-Paket konnte nicht geladen werden: ",
  pro_more: "Pro-Lizenz: ab 900 CHF pro Jahr und Organisation - siehe Preise.",
  protokoll_btn: "Prüfprotokoll (PDF)",
  protokoll_name: "Pruefprotokoll",
});
Object.assign(I18N.fr, {
  pro_title: "meldbar Pro",
  pro_intro: "Avec une licence Pro, l'application établit pour chaque contrôle et chaque déclaration créée un procès-verbal de contrôle en PDF : hash du fichier, déclaration, résultat, constatations, chaque règle vérifiée, identifiants et hashs du fichier envoyé - pour le dossier du véhicule. La clé de licence n'est conservée que dans ce navigateur ; le paquet Pro est chargé chiffré depuis cette page et déchiffré ici.",
  pro_key_label: "Clé de licence",
  pro_activate: "Activer",
  pro_remove: "Retirer la licence",
  pro_working: "Chargement du paquet Pro …",
  pro_active: "Pro actif pour {holder} · valable jusqu'au {until} · {n} véhicules",
  pro_grace: "La licence Pro de {holder} a expiré le {until} - encore {days} jours utilisables. Merci de la renouveler.",
  pro_expired: "La licence Pro de {holder} a expiré le {until}.",
  pro_bad_key: "Clé invalide (forme : MB1-XXXXX-XXXXX-XXXXX-XXXXX).",
  pro_unknown: "Cette clé n'est pas connue sur cette page. Faute de frappe ? Les nouvelles licences sont actives après la prochaine publication de la page.",
  pro_offline: "Le paquet Pro n'est pas en cache et la page est hors ligne. Activez-la une fois en ligne.",
  pro_failed: "Le paquet Pro n'a pas pu être chargé : ",
  pro_more: "Licence Pro : dès 900 CHF par an et par organisation - voir les prix.",
  protokoll_btn: "Procès-verbal (PDF)",
  protokoll_name: "Proces-verbal",
});
Object.assign(I18N.it, {
  pro_title: "meldbar Pro",
  pro_intro: "Con una licenza Pro l'app redige per ogni verifica e per ogni comunicazione creata un protocollo di verifica in PDF: hash del file, comunicazione, risultato, rilievi, ogni regola verificata, identificativi e hash del file inviato - per il dossier del veicolo. La chiave di licenza è conservata solo in questo browser; il pacchetto Pro viene caricato cifrato da questa pagina e decifrato qui.",
  pro_key_label: "Chiave di licenza",
  pro_activate: "Attiva",
  pro_remove: "Rimuovi licenza",
  pro_working: "Caricamento del pacchetto Pro …",
  pro_active: "Pro attivo per {holder} · valido fino al {until} · {n} veicoli",
  pro_grace: "La licenza Pro di {holder} è scaduta il {until} - utilizzabile ancora {days} giorni. Rinnovarla.",
  pro_expired: "La licenza Pro di {holder} è scaduta il {until}.",
  pro_bad_key: "Chiave non valida (forma: MB1-XXXXX-XXXXX-XXXXX-XXXXX).",
  pro_unknown: "Questa chiave non è nota su questa pagina. Errore di battitura? Le nuove licenze sono attive dopo la prossima pubblicazione della pagina.",
  pro_offline: "Il pacchetto Pro non è nella cache e la pagina è offline. Attivarla una volta online.",
  pro_failed: "Impossibile caricare il pacchetto Pro: ",
  pro_more: "Licenza Pro: da 900 CHF all'anno per organizzazione - vedi prezzi.",
  protokoll_btn: "Protocollo di verifica (PDF)",
  protokoll_name: "Protocollo-di-verifica",
});

const PRO = { active: false, meta: null, state: null };
const PRO_STORE = "meldbar-licence";
const PRO_CACHE = "aeoi-pro";
const PRO_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
const PRO_MAGIC = [0x4d, 0x42, 0x50, 0x31]; // "MBP1"
const enc = new TextEncoder();

// ---------- derivations (mirror of meldbar_pro/licence.py; test vectors in its tests) ----------
function proNormalise(key) {
  const compact = String(key || "").replace(/[\s-]/g, "").toUpperCase();
  if (!compact.startsWith("MB1")) throw new Error("bad_key");
  const body = compact.slice(3);
  if (body.length !== 20 || [...body].some((c) => !PRO_ALPHABET.includes(c))) throw new Error("bad_key");
  return body;
}
const hex = (buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
async function proBlobId(secret) {
  const k = await crypto.subtle.importKey("raw", enc.encode("meldbar-pro/blob-id"), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return hex(await crypto.subtle.sign("HMAC", k, enc.encode(secret))).slice(0, 24);
}
async function proAesKey(secret) {
  const ikm = await crypto.subtle.importKey("raw", enc.encode(secret), "HKDF", false, ["deriveKey"]);
  return crypto.subtle.deriveKey(
    { name: "HKDF", hash: "SHA-256", salt: enc.encode("meldbar-pro/v1"), info: enc.encode("aes-256-gcm") },
    ikm, { name: "AES-GCM", length: 256 }, false, ["decrypt"],
  );
}
async function proDecrypt(secret, blob) {
  const bytes = new Uint8Array(blob);
  if (bytes.length < 32 || PRO_MAGIC.some((b, i) => bytes[i] !== b)) throw new Error("not_a_bundle");
  const blobId = await proBlobId(secret);
  const plain = new Uint8Array(await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: bytes.slice(4, 16), additionalData: enc.encode(blobId) }, await proAesKey(secret), bytes.slice(16),
  ));
  const n = new DataView(plain.buffer).getUint32(0, false);
  const meta = JSON.parse(new TextDecoder().decode(plain.slice(4, 4 + n)));
  return { meta, wheel: plain.slice(4 + n) };
}

// ---------- fetching (own origin only; Cache API for offline use) ----------
async function proFetchBlob(blobId) {
  const url = new URL(`pro/${blobId}.bin`, location.href).href;
  let cache = null;
  try { cache = await caches.open(PRO_CACHE); } catch (e) { /* no Cache API (private window) */ }
  if (cache) { const hit = await cache.match(url); if (hit) return hit.arrayBuffer(); }
  let res;
  try { res = await fetch(url, { cache: "no-store" }); } catch (e) { throw new Error(navigator.onLine === false ? "offline" : "unknown"); }
  if (!res.ok) throw new Error("unknown");
  if (cache) { try { await cache.put(url, res.clone()); } catch (e) { /* ignore */ } }
  return res.arrayBuffer();
}

// ---------- activation ----------
function proStatus(meta) {
  const until = new Date(meta.valid_until + "T23:59:59");
  const now = new Date();
  if (now <= until) return { state: "valid", days: 0 };
  const days = 30 - Math.floor((now - until) / 86400000);
  return days > 0 ? { state: "grace", days } : { state: "expired", days: 0 };
}
function fmtDate(iso) { const [y, m, d] = iso.split("-"); return `${d}.${m}.${y}`; }

async function proActivate(key, { store = true } = {}) {
  const st = $("pro-status");
  st.className = "small";
  try {
    const secret = proNormalise(key);
    st.textContent = t("pro_working");
    const { meta, wheel } = await proDecrypt(secret, await proFetchBlob(await proBlobId(secret)));
    const { state, days } = proStatus(meta);
    PRO.meta = meta; PRO.state = state;
    if (state === "expired") {
      st.textContent = t("pro_expired", { holder: meta.holder, until: fmtDate(meta.valid_until) });
      st.className = "small msg-err";
      PRO.active = false;
    } else {
      const wheelName = /^[\w.-]+\.whl$/.test(meta.wheel || "") ? meta.wheel : "meldbar_pro-0-py3-none-any.whl"; // micropip reads name and tags from the file name
      py.FS.writeFile("/tmp/" + wheelName, wheel);
      const micropip = py.pyimport("micropip");
      await micropip.install("emfs:/tmp/" + wheelName, { deps: false });
      py.runPython(PRO_GLUE);
      PRO.active = true;
      st.textContent = state === "grace"
        ? t("pro_grace", { holder: meta.holder, until: fmtDate(meta.valid_until), days })
        : t("pro_active", { holder: meta.holder, until: fmtDate(meta.valid_until), n: meta.vehicles });
      st.className = "small " + (state === "grace" ? "msg-warn" : "msg-ok");
    }
    if (store) { try { localStorage.setItem(PRO_STORE, secret); } catch (e) { /* ignore */ } }
    $("pro-key").value = "";
    $("pro-form").classList.toggle("hidden", PRO.active);
    $("pro-remove").classList.toggle("hidden", !PRO.active);
    document.dispatchEvent(new CustomEvent("aeoi:pro", { detail: PRO }));
    console.info("aeoi:pro " + (PRO.active ? "active " + state : state));
  } catch (e) {
    PRO.active = false;
    const code = e && e.message;
    st.textContent = code === "bad_key" ? t("pro_bad_key") : code === "unknown" ? t("pro_unknown") : code === "offline" ? t("pro_offline") : t("pro_failed") + e;
    st.className = "small msg-err";
    console.info("aeoi:pro " + (code || "error"));
  }
}

function proRemove() {
  try { localStorage.removeItem(PRO_STORE); } catch (e) { /* ignore */ }
  PRO.active = false; PRO.meta = null; PRO.state = null;
  $("pro-status").textContent = ""; $("pro-status").className = "small";
  $("pro-form").classList.remove("hidden"); $("pro-remove").classList.add("hidden");
  document.dispatchEvent(new CustomEvent("aeoi:pro", { detail: PRO }));
}

// Python side: a thin adapter that hands the page's objects to the pack. The pack decides what
// the protocol contains.
const PRO_GLUE = `
import json
import meldbar_pro
from meldbar_pro import protokoll as _pro_protokoll

def pro_version():
    return meldbar_pro.__version__

def pro_protokoll_report(meta_json, lang):
    data = overview.report_dict(last_report, lang)
    out = _pro_protokoll.from_dict(data, json.loads(meta_json), lang)
    open("/tmp/protokoll.pdf", "wb").write(out)
    return "/tmp/protokoll.pdf"

def pro_protokoll_built(i, meta_json, lang):
    meta = json.loads(meta_json)
    meta["built"] = _pro_protokoll.built_meta(last_built[i], public_key_pem=last_built_pem or None)
    data = overview.report_dict(last_built_report, lang)
    out = _pro_protokoll.from_dict(data, meta, lang)
    open("/tmp/protokoll.pdf", "wb").write(out)
    return "/tmp/protokoll.pdf"
`;

// ---------- protocol buttons ----------
function localIso() {
  const d = new Date();
  const off = -d.getTimezoneOffset();
  const p = (n) => String(Math.abs(n)).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}${off >= 0 ? "+" : "-"}${p(Math.floor(Math.abs(off) / 60))}:${p(Math.abs(off) % 60)}`;
}
function proMeta(file) {
  return JSON.stringify({
    holder: PRO.meta.holder,
    licence_id: PRO.meta.licence_id,
    file_name: file.name,
    file_size: file.size || 0,
    file_sha256: file.sha256 || "",
    created: localIso(),
    aeoi_version: $("ver").textContent,
    test: !!file.test,
  });
}
function proDownloadPdf(path, stem) {
  const bytes = py.FS.readFile(path);
  const blob = new Blob([bytes], { type: "application/pdf" });
  const a = el("a", { href: URL.createObjectURL(blob), download: `${t("protokoll_name")}-${stem}.pdf` });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  console.info("aeoi:protokoll " + a.download + " " + bytes.length);
}
function proButton(onclick) {
  return el("button", { class: "btn pro", type: "button", onclick }, el("span", { text: t("protokoll_btn") }));
}

document.addEventListener("aeoi:rendered", (ev) => {
  const old = $("protokoll"); if (old) old.remove();
  if (!PRO.active || !ev.detail) return;
  const btn = proButton(() => proDownloadPdf(py.globals.get("pro_protokoll_report")(proMeta(last), LANG), last.name.replace(/\.[^.]+$/, "")));
  btn.id = "protokoll";
  $("download").after(btn);
});
document.addEventListener("aeoi:built", (ev) => {
  if (!PRO.active) return;
  ev.detail.views.forEach((v, i) => {
    const card = ev.detail.cards[i];
    card.querySelector(".actions").append(proButton(() => proDownloadPdf(
      py.globals.get("pro_protokoll_built")(i, proMeta({ name: ev.detail.file.name, size: ev.detail.file.size, sha256: ev.detail.file.sha256, test: ev.detail.test }), LANG),
      v.message_ref_id.slice(-8),
    )));
  });
});
document.addEventListener("aeoi:pro", () => { if (last && PRO.active) document.dispatchEvent(new CustomEvent("aeoi:rendered", { detail: last })); });

// ---------- wiring ----------
document.addEventListener("aeoi:booted", () => {
  $("pro-activate").disabled = false;
  let saved = null;
  try { saved = localStorage.getItem(PRO_STORE); } catch (e) { /* ignore */ }
  if (saved) proActivate(saved, { store: false });
});
$("pro-activate").addEventListener("click", () => proActivate($("pro-key").value));
$("pro-key").addEventListener("keydown", (ev) => { if (ev.key === "Enter") { ev.preventDefault(); proActivate($("pro-key").value); } });
$("pro-remove").addEventListener("click", proRemove);
