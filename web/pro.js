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
  mand_title: "Mandantenübersicht",
  mand_intro: "Alle Vehikel auf einen Blick: Wählen Sie den Ordner (Chrome, Edge) oder die Dateien, in denen Ihre Workbooks und Register liegen - ein Vehikel = «Name.xlsx» + «Name.sqlite». Die Tabelle zeigt pro Vehikel die Prüfung des Workbooks, den Stand des Registers und was gesendet würde. «Alle bereiten Vehikel erstellen» baut, verschlüsselt und protokolliert jede fällige Meldung und aktualisiert die Register - im Ordner direkt, sonst als Zip. Nichts verlässt den Browser.",
  mand_folder: "Ordner wählen",
  mand_files: "Dateien wählen",
  mand_mode: "Meldungen",
  mand_mode_test: "Testmeldungen",
  mand_mode_prod: "produktiv",
  mand_key: "ESTV-Schlüssel für alle",
  mand_key_set: "Schlüssel für alle Vehikel gesetzt",
  mand_refresh: "Neu prüfen",
  mand_build: "Alle bereiten Vehikel erstellen",
  mand_reading: "{n} Dateien werden gelesen …",
  mand_overview: "{v} Vehikel · {r} bereit · {e} mit Fehlern · {p} ohne Portal-Ergebnis · {n} ohne Register",
  mand_building: "Meldungen werden erstellt …",
  mand_built: "{m} Meldung(en) für {v} Vehikel erstellt, {s} übersprungen, {e} Fehler",
  mand_written: "Ausgaben im Ordner «{dir}», Register aktualisiert.",
  mand_zipped: "Zip heruntergeladen: Ausgaben pro Vehikel und die aktualisierten Register unter «Register/» - diese ersetzen Ihre bisherigen Registerdateien.",
  mand_nothing: "Kein Vehikel ist bereit.",
  mand_no_files: "Keine Workbooks (.xlsx) oder Register (.sqlite) gefunden.",
  mand_col_vehicle: "Vehikel",
  mand_col_check: "Workbook",
  mand_col_registry: "Register",
  mand_col_plan: "Zu senden",
  mand_col_state: "Status",
  mand_check_ok: "OK",
  mand_check_bad: "{n} Fehler",
  mand_no_workbook: "-",
  mand_no_registry: "kein Register",
  mand_plan: { new: "neu", changed: "geändert", deleted: "Storno", unchanged: "unverändert", blocked: "blockiert" },
  mand_pending: "{n} offen",
  mand_error: "Fehler: ",
  mand_paired: "Register «{file}» über die ESTV-ID zugeordnet",
  mand_quick_ok: "akzeptiert",
  mand_quick_bad: "abgelehnt",
  mand_quick_title: "Ergebnis des Portals für {ref} ohne Text erfassen",
  mand_oc_title: "Portal-Ergebnisse erfassen",
  mand_oc_hint: "Validierungsbestätigungen oder Statusmeldungen (XML oder Text) für beliebig viele Vehikel auf einmal - jede wird über ihre MessageRefId oder DocRefId der richtigen Meldung zugeordnet.",
  mand_oc_files: "Ergebnisdateien wählen",
  mand_oc_paste: "… oder den Text aus dem Portal hier einfügen",
  mand_oc_record: "Zuordnen und erfassen",
  mand_oc_done: "{r} Ergebnis(se) erfasst, {u} nicht zuzuordnen.",
  mand_oc_row: "{file} → {fi} · {ref} · {status}",
  mand_save: "Geänderte Register herunterladen",
  mand_saved_dir: "Register im Ordner aktualisiert.",
  mand_unsaved: "Register geändert, noch nicht gespeichert: {n}",
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
  mand_title: "Vue d'ensemble des mandats",
  mand_intro: "Tous les véhicules d'un coup d'œil : choisissez le dossier (Chrome, Edge) ou les fichiers où se trouvent vos classeurs et registres - un véhicule = « Nom.xlsx » + « Nom.sqlite ». Le tableau montre par véhicule le contrôle du classeur, l'état du registre et ce qui serait envoyé. « Créer tous les véhicules prêts » construit, chiffre et documente chaque déclaration due et met à jour les registres - directement dans le dossier, sinon en zip. Rien ne quitte le navigateur.",
  mand_folder: "Choisir le dossier",
  mand_files: "Choisir les fichiers",
  mand_mode: "Déclarations",
  mand_mode_test: "de test",
  mand_mode_prod: "productives",
  mand_key: "Clé AFC pour tous",
  mand_key_set: "Clé définie pour tous les véhicules",
  mand_refresh: "Revérifier",
  mand_build: "Créer tous les véhicules prêts",
  mand_reading: "Lecture de {n} fichiers …",
  mand_overview: "{v} véhicules · {r} prêts · {e} avec erreurs · {p} sans résultat du portail · {n} sans registre",
  mand_building: "Création des déclarations …",
  mand_built: "{m} déclaration(s) créée(s) pour {v} véhicules, {s} ignorés, {e} erreurs",
  mand_written: "Résultats dans le dossier « {dir} », registres mis à jour.",
  mand_zipped: "Zip téléchargé : résultats par véhicule et registres mis à jour sous « Register/ » - ils remplacent vos anciens fichiers de registre.",
  mand_nothing: "Aucun véhicule n'est prêt.",
  mand_no_files: "Aucun classeur (.xlsx) ni registre (.sqlite) trouvé.",
  mand_col_vehicle: "Véhicule",
  mand_col_check: "Classeur",
  mand_col_registry: "Registre",
  mand_col_plan: "À envoyer",
  mand_col_state: "État",
  mand_check_ok: "OK",
  mand_check_bad: "{n} erreurs",
  mand_no_workbook: "-",
  mand_no_registry: "pas de registre",
  mand_plan: { new: "nouveau", changed: "modifié", deleted: "annulation", unchanged: "inchangé", blocked: "bloqué" },
  mand_pending: "{n} en attente",
  mand_error: "Erreur : ",
  mand_paired: "Registre « {file} » associé par l'ID AFC",
  mand_quick_ok: "acceptée",
  mand_quick_bad: "rejetée",
  mand_quick_title: "Saisir le résultat du portail pour {ref} sans texte",
  mand_oc_title: "Saisir les résultats du portail",
  mand_oc_hint: "Confirmations de validation ou messages de statut (XML ou texte) pour autant de véhicules que vous voulez, d'un coup - chacun est associé à la bonne déclaration par son MessageRefId ou un DocRefId.",
  mand_oc_files: "Choisir les fichiers de résultats",
  mand_oc_paste: "… ou coller ici le texte du portail",
  mand_oc_record: "Associer et saisir",
  mand_oc_done: "{r} résultat(s) saisi(s), {u} sans correspondance.",
  mand_oc_row: "{file} → {fi} · {ref} · {status}",
  mand_save: "Télécharger les registres modifiés",
  mand_saved_dir: "Registres mis à jour dans le dossier.",
  mand_unsaved: "Registres modifiés, pas encore enregistrés : {n}",
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
  mand_title: "Panoramica dei mandati",
  mand_intro: "Tutti i veicoli in un colpo d'occhio: scelga la cartella (Chrome, Edge) o i file dove stanno i suoi workbook e registri - un veicolo = «Nome.xlsx» + «Nome.sqlite». La tabella mostra per veicolo la verifica del workbook, lo stato del registro e cosa verrebbe inviato. «Crea tutti i veicoli pronti» costruisce, cifra e protocolla ogni comunicazione dovuta e aggiorna i registri - direttamente nella cartella, altrimenti in uno zip. Nulla lascia il browser.",
  mand_folder: "Scegli cartella",
  mand_files: "Scegli file",
  mand_mode: "Comunicazioni",
  mand_mode_test: "di prova",
  mand_mode_prod: "produttive",
  mand_key: "Chiave AFC per tutti",
  mand_key_set: "Chiave impostata per tutti i veicoli",
  mand_refresh: "Verifica di nuovo",
  mand_build: "Crea tutti i veicoli pronti",
  mand_reading: "Lettura di {n} file …",
  mand_overview: "{v} veicoli · {r} pronti · {e} con errori · {p} senza esito del portale · {n} senza registro",
  mand_building: "Creazione delle comunicazioni …",
  mand_built: "{m} comunicazione/i creata/e per {v} veicoli, {s} saltati, {e} errori",
  mand_written: "Output nella cartella «{dir}», registri aggiornati.",
  mand_zipped: "Zip scaricato: output per veicolo e registri aggiornati in «Register/» - sostituiscono i suoi file di registro precedenti.",
  mand_nothing: "Nessun veicolo è pronto.",
  mand_no_files: "Nessun workbook (.xlsx) o registro (.sqlite) trovato.",
  mand_col_vehicle: "Veicolo",
  mand_col_check: "Workbook",
  mand_col_registry: "Registro",
  mand_col_plan: "Da inviare",
  mand_col_state: "Stato",
  mand_check_ok: "OK",
  mand_check_bad: "{n} errori",
  mand_no_workbook: "-",
  mand_no_registry: "nessun registro",
  mand_plan: { new: "nuovo", changed: "modificato", deleted: "storno", unchanged: "invariato", blocked: "bloccato" },
  mand_pending: "{n} in sospeso",
  mand_error: "Errore: ",
  mand_paired: "Registro «{file}» abbinato tramite l'ID AFC",
  mand_quick_ok: "accettata",
  mand_quick_bad: "respinta",
  mand_quick_title: "Registrare l'esito del portale per {ref} senza testo",
  mand_oc_title: "Registrare gli esiti del portale",
  mand_oc_hint: "Conferme di validazione o messaggi di stato (XML o testo) per quanti veicoli vuole, in una volta - ognuno viene abbinato alla comunicazione giusta tramite il suo MessageRefId o un DocRefId.",
  mand_oc_files: "Scegli i file degli esiti",
  mand_oc_paste: "… oppure incolli qui il testo del portale",
  mand_oc_record: "Abbina e registra",
  mand_oc_done: "{r} esito/i registrato/i, {u} non abbinabili.",
  mand_oc_row: "{file} → {fi} · {ref} · {status}",
  mand_save: "Scarica i registri modificati",
  mand_saved_dir: "Registri aggiornati nella cartella.",
  mand_unsaved: "Registri modificati, non ancora salvati: {n}",
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

import os, shutil, datetime as _dt
from meldbar_pro import mandanten as _pro_mandanten
MAND_IN, MAND_OUT = "/tmp/mandanten/in", "/tmp/mandanten/out"

def pro_mandanten_reset():
    shutil.rmtree("/tmp/mandanten", ignore_errors=True)
    os.makedirs(MAND_IN); os.makedirs(MAND_OUT)
    return MAND_IN

def pro_mandanten_overview(names_json, version, test, lang):
    paths = [os.path.join(MAND_IN, n) for n in json.loads(names_json)]
    return json.dumps(_pro_mandanten.overview(paths, version, test, lang))

def pro_mandanten_build(names_json, version, test, lang, pem, header, meta_json):
    meta = json.loads(meta_json)
    paths = [os.path.join(MAND_IN, n) for n in json.loads(names_json)]
    shutil.rmtree(MAND_OUT, ignore_errors=True); os.makedirs(MAND_OUT)
    m = _pro_mandanten.batch_build(paths, MAND_OUT, version, test, lang=lang, public_key=pem or None, header=header,
                                   holder=meta["holder"], licence_id=meta["licence_id"], created=_dt.datetime.fromisoformat(meta["created"]))
    m["registries"] = {r["stem"]: r["registry"] for r in m["vehicles"] if r["built"] and r["registry"]}
    return json.dumps(m)

def pro_mandanten_zip(manifest_json):
    m = json.loads(manifest_json)
    return str(_pro_mandanten.zip_outputs(m, m["registries"], "/tmp/mandanten/Stapel.zip"))

def pro_mandanten_outcomes(names_json, outcomes_json, lang):
    paths = [os.path.join(MAND_IN, n) for n in json.loads(names_json)]
    outcomes = [(o["name"], o["text"]) for o in json.loads(outcomes_json)]
    return json.dumps(_pro_mandanten.record_outcomes(paths, outcomes, lang))

def pro_mandanten_manual(names_json, stem, ref, accepted, lang):
    paths = [os.path.join(MAND_IN, n) for n in json.loads(names_json)]
    return json.dumps(_pro_mandanten.record_manual(paths, stem, ref, bool(accepted), lang))

def pro_mandanten_zip_registries(paths_json):
    import zipfile
    p = "/tmp/mandanten/Register.zip"
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
        for path in json.loads(paths_json):
            z.write(path, "Register/" + os.path.basename(path))
    return p
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

// ---------- Mandantenübersicht + Stapelverarbeitung (Pro) ----------
// Files come from a folder (File System Access API: outputs and registries are written back in
// place) or from a multi-file input (outputs and updated registries leave as one zip). The
// page only moves bytes and renders JSON; what a vehicle needs and what gets built is decided
// by the Pro package.
const MAND = { dir: null, files: new Map(), pem: "" }; // files: name -> { bytes, handle? }
const MAND_FSA = typeof window.showDirectoryPicker === "function" && !location.hash.includes("nofsa");
const mandSuffix = (name) => /\.(xlsx|xlsm|sqlite|db)$/i.test(name);

async function mandLoadFromDir(dir) {
  MAND.dir = dir; MAND.files = new Map();
  for await (const [name, h] of dir.entries()) {
    if (h.kind === "file" && mandSuffix(name)) MAND.files.set(name, { bytes: new Uint8Array(await (await h.getFile()).arrayBuffer()), handle: h });
  }
  await mandOverview();
}
async function mandLoadFromFiles(list) {
  MAND.dir = null; MAND.files = new Map();
  for (const f of list) if (mandSuffix(f.name)) MAND.files.set(f.name, { bytes: new Uint8Array(await f.arrayBuffer()) });
  await mandOverview();
}
function mandStage() {
  const dir = py.globals.get("pro_mandanten_reset")();
  for (const [name, f] of MAND.files) py.FS.writeFile(`${dir}/${name}`, f.bytes);
  return JSON.stringify([...MAND.files.keys()]);
}
const mandTest = () => $("mand-mode").value === "test";
const mandHeader = () => ($("version").value === "3.0" ? $("build-header").value : "oecd");

async function mandOverview() {
  const st = $("mand-status");
  if (!MAND.files.size) { st.textContent = t("mand_no_files"); st.className = "small msg-err"; $("mand-table").replaceChildren(); return; }
  st.textContent = t("mand_reading", { n: MAND.files.size }); st.className = "small";
  $("mand-refresh").disabled = $("mand-build").disabled = true;
  await nextPaint();
  try {
    const names = mandStage();
    const ov = JSON.parse(py.globals.get("pro_mandanten_overview")(names, $("version").value, mandTest(), LANG));
    mandRender(ov);
    const tt = ov.totals;
    st.textContent = t("mand_overview", { v: tt.vehicles, r: tt.ready, e: tt.with_errors, p: tt.pending, n: tt.without_registry });
    st.className = "small " + (tt.with_errors ? "msg-warn" : "msg-ok");
    $("mand-build").disabled = tt.ready === 0;
    $("mand-oc-record").disabled = false;
    console.info(`aeoi:mandanten overview ${tt.vehicles} ready=${tt.ready}`);
  } catch (e) {
    st.textContent = t("mand_error") + e; st.className = "small msg-err";
    console.info("aeoi:mandanten error");
  } finally { $("mand-refresh").disabled = false; }
}

function mandRender(ov) {
  const table = el("table");
  table.append(el("tr", {}, ...["mand_col_vehicle", "mand_col_check", "mand_col_registry", "mand_col_plan", "mand_col_state"].map((k) => el("th", { text: t(k) }))));
  const labels = I18N[LANG].mand_plan || I18N.de.mand_plan;
  for (const v of ov.vehicles) {
    const tr = el("tr", { class: v.ready ? "ready" : v.check_ok === false ? "bad" : "idle" });
    const who = el("td", {}, el("strong", { text: v.fi_name || (v.registry_fi && v.registry_fi.name) || v.stem }), el("div", { class: "small muted", text: (v.estv_id ? v.estv_id + " · " : "") + v.stem }));
    if (v.paired_by === "estv_id" && v.registry) who.append(el("span", { class: "paired", text: t("mand_paired", { file: v.registry.split("/").pop() }) }));
    tr.append(who);
    tr.append(el("td", {}, v.workbook === null ? t("mand_no_workbook") : el("span", { class: "mini " + (v.check_ok ? "ok" : "err"), text: v.check_ok ? t("mand_check_ok") : t("mand_check_bad", { n: v.check_errors + v.check_inputs }) })));
    const reg = el("td");
    if (v.registry === null) reg.textContent = t("mand_no_registry");
    else {
      for (const [status, n] of Object.entries(v.counts)) reg.append(el("span", { class: "mini " + status, text: `${n} ${status}` }));
      if (v.pending.length) reg.append(el("span", { class: "mini pending", text: t("mand_pending", { n: v.pending.length }) }));
      for (const ref of v.pending) {
        const q = el("span", { class: "quick", title: t("mand_quick_title", { ref }) });
        q.append(el("button", { class: "btn", type: "button", text: "✓ " + t("mand_quick_ok"), onclick: () => mandManual(v.stem, ref, true) }));
        q.append(el("button", { class: "btn", type: "button", text: "✗ " + t("mand_quick_bad"), onclick: () => mandManual(v.stem, ref, false) }));
        reg.append(el("div", { class: "small mono", text: ref.slice(-12) }, q));
      }
      if (!Object.keys(v.counts).length) reg.append(el("span", { class: "muted small", text: "0" }));
    }
    tr.append(reg);
    const plan = el("td");
    if (v.plan) for (const k of ["new", "changed", "deleted", "unchanged", "blocked"]) {
      const n = v.plan[k === "deleted" ? "deletions" : k];
      if (n) plan.append(el("span", { class: "mini " + k, text: `${n} ${labels[k]}` }));
    }
    tr.append(plan);
    tr.append(el("td", { class: "reason", text: v.reason }));
    table.append(tr);
  }
  $("mand-table").replaceChildren(table);
}

async function mandBuild() {
  const st = $("mand-status");
  st.textContent = t("mand_building"); st.className = "small";
  $("mand-build").disabled = $("mand-refresh").disabled = true;
  $("mand-out").replaceChildren();
  await nextPaint();
  try {
    const names = mandStage();
    const meta = JSON.stringify({ holder: PRO.meta.holder, licence_id: PRO.meta.licence_id, created: localIso() });
    const m = JSON.parse(py.globals.get("pro_mandanten_build")(names, $("version").value, mandTest(), LANG, MAND.pem, mandHeader(), meta));
    const tt = m.totals;
    const stamp = m.created.slice(0, 16).replace("T", " ").replace(":", "");
    let note = "";
    if (MAND.dir) {
      const dirName = `Meldungen ${stamp}`;
      const outDir = await MAND.dir.getDirectoryHandle(dirName, { create: true });
      for (const r of m.vehicles) {
        if (!r.built.length) continue;
        const sub = await outDir.getDirectoryHandle(r.stem, { create: true });
        for (const b of r.built) for (const path of Object.values(b.files)) {
          const w = await (await sub.getFileHandle(path.split("/").pop(), { create: true })).createWritable();
          await w.write(py.FS.readFile(path)); await w.close();
        }
        const regName = m.registries[r.stem] && m.registries[r.stem].split("/").pop();
        const src = regName && MAND.files.get(regName);
        if (src && src.handle) { const w = await src.handle.createWritable(); await w.write(py.FS.readFile(m.registries[r.stem])); await w.close(); }
      }
      note = t("mand_written", { dir: dirName });
    } else if (tt.built) {
      const zip = py.globals.get("pro_mandanten_zip")(JSON.stringify(m));
      download(py.FS.readFile(zip), `Stapel-${stamp.replace(" ", "-")}.zip`, "application/zip");
      note = t("mand_zipped");
      for (const path of Object.values(m.registries)) { // the session goes on with the updated registries
        const entry = MAND.files.get(path.split("/").pop());
        if (entry) entry.bytes = py.FS.readFile(path);
      }
    }
    for (const r of m.vehicles) {
      if (!r.built.length && !r.error) continue;
      const card = el("div", { class: "built" });
      card.append(el("div", { class: "head" }, el("span", { text: r.fi_name || r.stem }), r.error ? el("span", { class: "msg-err", text: t("mand_error") + r.error }) : null));
      for (const b of r.built) {
        const kind = b.kind === "correction" ? t("kind_correction") : t("kind_new");
        const enc = b.encrypted ? "" : " · " + t("built_unencrypted");
        card.append(el("div", { class: "ref", text: `${kind} · ${t("built_records", { n: b.records })} · ${b.message_ref_id}${enc}` }));
      }
      $("mand-out").append(card);
    }
    const summary = t("mand_built", { m: tt.built, v: tt.vehicles_built, s: tt.skipped, e: tt.errors }) + (note ? " " + note : "");
    $("mand-out").prepend(el("div", { class: "next " + (tt.errors ? "msg-warn" : "msg-ok"), text: summary }));
    console.info(`aeoi:mandanten built ${tt.built} vehicles=${tt.vehicles_built} errors=${tt.errors}`);
    if (MAND.dir) await mandLoadFromDir(MAND.dir); // registries changed on disk: re-read, fresh overview
    else if (MAND.files.size) await mandOverview(); // in-memory registries updated: fresh overview
  } catch (e) {
    st.textContent = t("mand_error") + e; st.className = "small msg-err";
    console.info("aeoi:mandanten error");
  } finally { $("mand-refresh").disabled = false; }
}

// Registries changed by an outcome: written back into the folder, or kept in memory (the
// staged copy is re-read from the runtime) until "Geänderte Register herunterladen" zips them.
MAND.dirty = new Set();
async function mandPersistRegistries(registries) {
  for (const [stem, path] of Object.entries(registries)) {
    const name = path.split("/").pop();
    const bytes = py.FS.readFile(path);
    const entry = MAND.files.get(name);
    if (entry) entry.bytes = bytes;
    if (MAND.dir && entry && entry.handle) { const w = await entry.handle.createWritable(); await w.write(bytes); await w.close(); }
    else MAND.dirty.add(name);
  }
  $("mand-save").classList.toggle("hidden", MAND.dirty.size === 0);
  if (MAND.dirty.size) $("mand-save").querySelector("span").textContent = t("mand_save") + ` (${MAND.dirty.size})`;
  return MAND.dir ? t("mand_saved_dir") : t("mand_unsaved", { n: MAND.dirty.size });
}
async function mandRecordOutcomes() {
  const st = $("mand-status");
  const items = [];
  for (const f of $("mand-oc-files").files) items.push({ name: f.name, text: await f.text() });
  const pasted = $("mand-oc-text").value.trim();
  if (pasted) items.push({ name: t("mand_oc_paste").replace(/^… /, "").slice(0, 24) + " …", text: pasted });
  if (!items.length) return;
  $("mand-oc-record").disabled = true;
  await nextPaint();
  try {
    const names = mandStage();
    const res = JSON.parse(py.globals.get("pro_mandanten_outcomes")(names, JSON.stringify(items), LANG));
    const out = $("mand-oc-out"); out.replaceChildren();
    for (const r of res.rows) {
      const line = r.error ? `${r.file}: ${r.error}` : t("mand_oc_row", { file: r.file, fi: r.fi_name || r.stem, ref: r.message_ref_id, status: r.status });
      out.append(el("div", { class: "built " + (r.error ? "msg-err" : ""), text: line }));
    }
    const note = await mandPersistRegistries(res.registries);
    st.textContent = t("mand_oc_done", { r: res.totals.recorded, u: res.totals.unmatched }) + " " + note;
    st.className = "small " + (res.totals.unmatched ? "msg-warn" : "msg-ok");
    console.info(`aeoi:mandanten outcomes ${res.totals.recorded} unmatched=${res.totals.unmatched}`);
    $("mand-oc-text").value = ""; $("mand-oc-files").value = "";
    await mandOverview();
  } catch (e) {
    st.textContent = t("mand_error") + e; st.className = "small msg-err";
    console.info("aeoi:mandanten error");
  } finally { $("mand-oc-record").disabled = false; }
}
async function mandManual(stem, ref, accepted) {
  const st = $("mand-status");
  try {
    const names = mandStage();
    const res = JSON.parse(py.globals.get("pro_mandanten_manual")(names, stem, ref, accepted, LANG));
    const note = await mandPersistRegistries(res.registries);
    st.textContent = `${stem} · ${ref.slice(-12)} · ${res.status}. ${note}`;
    st.className = "small msg-ok";
    console.info(`aeoi:mandanten manual ${res.status}`);
    await mandOverview();
  } catch (e) {
    st.textContent = t("mand_error") + e; st.className = "small msg-err";
    console.info("aeoi:mandanten error");
  }
}
$("mand-oc-record").addEventListener("click", mandRecordOutcomes);
$("mand-oc-files").addEventListener("change", () => { $("mand-oc-record").disabled = !MAND.files.size; });
$("mand-oc-text").addEventListener("input", () => { $("mand-oc-record").disabled = !MAND.files.size; });
$("mand-save").addEventListener("click", () => {
  mandStage();
  const paths = [...MAND.dirty].map((n) => `/tmp/mandanten/in/${n}`);
  const zip = py.globals.get("pro_mandanten_zip_registries")(JSON.stringify(paths));
  download(py.FS.readFile(zip), `Register-${localIso().slice(0, 16).replace("T", "-").replace(":", "")}.zip`, "application/zip");
  MAND.dirty.clear(); $("mand-save").classList.add("hidden");
  console.info("aeoi:mandanten registries-zipped");
});

$("mand-folder").addEventListener("click", async () => {
  try { const dir = await window.showDirectoryPicker({ mode: "readwrite" }); await mandLoadFromDir(dir); } catch (e) { /* cancelled */ }
});
$("mand-files").addEventListener("change", (ev) => mandLoadFromFiles([...ev.target.files]));
$("mand-refresh").addEventListener("click", mandOverview);
$("mand-build").addEventListener("click", mandBuild);
$("mand-mode").addEventListener("change", () => { if (MAND.files.size) mandOverview(); });
$("mand-key").addEventListener("change", async (ev) => {
  const file = ev.target.files[0]; if (!file) return;
  try {
    py.globals.set("_key_bytes", new Uint8Array(await file.arrayBuffer()));
    MAND.pem = py.runPython("from aeoi.estv import packaging; packaging.public_key_pem(packaging.load_public_key(bytes(_key_bytes.to_py())))");
    $("mand-key-status").textContent = t("mand_key_set");
  } catch (e) { $("mand-key-status").textContent = t("key_bad") + e; }
});
document.addEventListener("aeoi:pro", () => {
  $("mand-card").classList.toggle("hidden", !PRO.active);
  $("mand-folder").classList.toggle("hidden", !MAND_FSA);
});
document.addEventListener("aeoi:language", () => { $("mand-oc-text").placeholder = t("mand_oc_paste"); if (PRO.active && MAND.files.size) mandOverview(); });
$("mand-oc-text").placeholder = t("mand_oc_paste");

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
