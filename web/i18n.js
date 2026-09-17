// Page texts in German, French and Italian. Own static strings only; "privacy_html" is the one
// key rendered as HTML (it carries <code> tags). The technical check messages come from the
// Python package and stay English; rule titles and remedies come from the package in the
// page language (rule_titles.json).
"use strict";

const I18N = {
  de: {
    title: "aeoi - CRS-Datei prüfen",
    tagline: "CRS-Prüfung im Browser",
    h1: "CRS-Datei prüfen, ohne etwas zu installieren",
    lead: "Schema 2.0 oder 3.0, die Regeln der Technischen Wegleitung AIA der ESTV, Zeichensatz, Partnerstaaten, IBAN/ISIN - geprüft in Ihrem Browser. Die Datei verlässt ihn nicht.",
    badge_rules: "59 von 65 ESTV-Regeln",
    badge_local: "Keine Datei verlässt den Browser",
    badge_open: "Open Source, Apache-2.0",
    boot_title: "Prüfumgebung",
    step1: "Laufzeit", step2: "Bibliotheken", step3: "Prüfregeln", step4: "Bereit",
    loading: "Laufzeit wird geladen … (einmalig etwa 20-40 MB, danach aus dem Browser-Cache)",
    libs: "Bibliotheken werden geladen …",
    rules: "Prüfregeln werden geladen …",
    ready: "Bereit. Ab jetzt findet keine Netzanfrage mehr statt.",
    boot_error: "Die Laufzeit konnte nicht geladen werden: ",
    input_title: "Datei prüfen",
    drop_title: "Datei hierher ziehen oder klicken",
    drop_hint: "CRS-XML (.xml) oder ausgefüllte aeoi-Excel-Vorlage (.xlsx) - Schema 2.0 oder 3.0 wird erkannt",
    version_label: "Schema-Version für Excel-Vorlagen",
    v3: "3.0 (ab 16.01.2027)", v2: "2.0 (bis 14.12.2026)",
    mode_label: "XML-Datei ist eine",
    mode_auto: "automatisch (Dateiname Test… = Testmeldung)", mode_test: "Testmeldung", mode_prod: "produktive Meldung",
    samples_label: "Ohne eigene Datei ausprobieren:",
    sample_ok: "Beispiel (gültig)", sample_bad: "Beispiel (mit Fehlern)", sample_xlsx: "Beispiel-Vorlage (Excel)",
    running: "Prüfung läuft …",
    check_error: "Fehler bei der Prüfung: ",
    download: "Bericht herunterladen", copy: "Bericht kopieren", copied: "Kopiert", again: "Weitere Datei prüfen",
    verdict_ok: "Die Datei besteht alle Prüfungen",
    verdict_bad: "Das Portal würde diese Datei abweisen",
    verdict_unreadable: "Die Datei konnte nicht gelesen werden",
    sub_xml: "CRS-XML, Schema {version} · geprüft in {time}",
    sub_workbook: "aeoi-Excel-Vorlage, Schema {version} · geprüft in {time}",
    stat_errors: "Fehler", stat_inputs: "Eingabefehler", stat_notes: "Hinweise", stat_accounts: "Konten", stat_persons: "natürliche Personen", stat_entities: "Rechtsträger", stat_cp: "beherrschende Personen",
    ov_title: "Inhalt der Meldung",
    ov_countries: "Ansässigkeit der Kontoinhaber",
    ov_note: "Anzahl Konten je Ansässigkeitsland des Kontoinhabers; ein Konto kann in mehreren Ländern zählen.",
    ov_none: "Keine Kontodaten lesbar.",
    kv_fi: "Meldendes Institut", kv_id: "ESTV-ID", kv_year: "Meldejahr", kv_type: "Meldungstyp", kv_balances: "Salden (Summe)", kv_flags: "Besonderheiten",
    type_CRS701: "Neumeldung (CRS701)", type_CRS702: "Korrekturmeldung (CRS702)", type_CRS703: "Nullmeldung (CRS703)",
    flag_closed: "{n} geschlossen", flag_undocumented: "{n} undokumentiert", flag_dormant: "{n} ruhend", flag_joint: "{n} Gemeinschaftskonten", flag_none: "keine",
    leg_individual: "natürliche Personen", leg_CRS101: "passive NFE mit beherrschenden Personen (CRS101)", leg_CRS102: "meldepflichtige Rechtsträger (CRS102)", leg_CRS103: "passive NFE, selbst meldepflichtig (CRS103)",
    findings_title: "Befunde",
    no_findings: "Keine Befunde. Die Datei besteht alle Prüfungen, die vor dem Portal möglich sind.",
    f_all: "Alle", f_error: "Fehler", f_input: "Eingabe", f_info: "Hinweise",
    loc_file: "Datei", loc_header: "Meldungskopf", loc_fi: "Meldendes Institut", loc_account: "Konto {ref}", loc_cp: "beherrschende Person {n}", loc_workbook: "Vorlage", loc_sheet: "Blatt {sheet}", loc_row: "Zeile {row}",
    fix_label: "Was tun", official_label: "Wortlaut der ESTV (Deutsch)", technical_label: "Technische Meldung",
    how_title: "So funktioniert es",
    how1_t: "Laden", how1: "Der Browser lädt einmalig eine Python-Laufzeit (Pyodide) und das Prüfpaket. Danach kommt alles aus dem Cache.",
    how2_t: "Prüfen", how2: "Die Datei wird im Speicher des Browsers gelesen: OECD-Schema, Header- und DocSpec-Regeln, Zeichensatz, Partnerstaaten des Meldejahrs, IBAN/ISIN, 3.0-Querbezüge.",
    how3_t: "Beheben", how3: "Jeder Befund nennt den ESTV-Code, die Stelle und was zu tun ist. Nur Transport, Entschlüsselung, Virenscan und Registrierung prüft allein das Portal.",
    privacy_title: "Datenschutz im Detail",
    privacy_html: "<strong>Ihre Datei verlässt den Browser nicht.</strong> Diese Seite ist statisch, ohne Analytics und ohne eigene Serverkomponente. Beim Laden wird nur diese Seite angefragt - Laufzeit, Bibliotheken und Prüfpaket liegen auf demselben Server, und der Host sieht den Seitenaufruf wie bei jeder Website. Nach dem ersten Besuch funktioniert die Seite auch offline. Nach der Dateiauswahl findet keine Netzanfrage statt - eine Content-Security-Policy der Seite lässt den Browser keine andere Adresse kontaktieren. Sprache, Farbschema und der Zugriff auf Ihr Register merkt sich der Browser lokal.",
    source: "Quelle und Regeln:", repo: "Repository aeoi", version: "Version",
    guidance: "Technische Wegleitung AIA der ESTV, September 2026",
    english_note: "Technische Meldungen auf Englisch, mit dem Fehlercode der ESTV",
    theme: "Farbschema: {mode}", theme_auto: "automatisch", theme_light: "hell", theme_dark: "dunkel",
    report_name: "aeoi-pruefbericht",
  },
  fr: {
    title: "aeoi - Vérifier un fichier CRS",
    tagline: "Vérification CRS dans le navigateur",
    h1: "Vérifier un fichier CRS, sans rien installer",
    lead: "Schéma 2.0 ou 3.0, les règles de la Directive technique EAR de l'AFC, jeu de caractères, États partenaires, IBAN/ISIN - vérifiés dans votre navigateur. Le fichier ne le quitte pas.",
    badge_rules: "59 des 65 règles de l'AFC",
    badge_local: "Aucun fichier ne quitte le navigateur",
    badge_open: "Open source, Apache-2.0",
    boot_title: "Environnement de vérification",
    step1: "Environnement", step2: "Bibliothèques", step3: "Règles", step4: "Prêt",
    loading: "Chargement de l'environnement … (une seule fois, environ 20-40 Mo, ensuite depuis le cache du navigateur)",
    libs: "Chargement des bibliothèques …",
    rules: "Chargement des règles …",
    ready: "Prêt. À partir de maintenant, plus aucune requête réseau.",
    boot_error: "L'environnement n'a pas pu être chargé : ",
    input_title: "Vérifier un fichier",
    drop_title: "Glissez le fichier ici ou cliquez",
    drop_hint: "CRS-XML (.xml) ou modèle Excel aeoi rempli (.xlsx) - le schéma 2.0 ou 3.0 est détecté",
    version_label: "Version du schéma pour les modèles Excel",
    v3: "3.0 (dès le 16.01.2027)", v2: "2.0 (jusqu'au 14.12.2026)",
    mode_label: "Le fichier XML est une",
    mode_auto: "automatique (nom Test… = déclaration test)", mode_test: "déclaration test", mode_prod: "déclaration productive",
    samples_label: "Essayer sans fichier à soi :",
    sample_ok: "Exemple (valide)", sample_bad: "Exemple (avec erreurs)", sample_xlsx: "Modèle d'exemple (Excel)",
    running: "Vérification en cours …",
    check_error: "Erreur lors de la vérification : ",
    download: "Télécharger le rapport", copy: "Copier le rapport", copied: "Copié", again: "Vérifier un autre fichier",
    verdict_ok: "Le fichier passe toutes les vérifications",
    verdict_bad: "Le portail rejetterait ce fichier",
    verdict_unreadable: "Le fichier n'a pas pu être lu",
    sub_xml: "CRS-XML, schéma {version} · vérifié en {time}",
    sub_workbook: "Modèle Excel aeoi, schéma {version} · vérifié en {time}",
    stat_errors: "Erreurs", stat_inputs: "Erreurs de saisie", stat_notes: "Remarques", stat_accounts: "Comptes", stat_persons: "personnes physiques", stat_entities: "entités", stat_cp: "personnes détenant le contrôle",
    ov_title: "Contenu de la déclaration",
    ov_countries: "Résidence des titulaires de compte",
    ov_note: "Nombre de comptes par pays de résidence du titulaire ; un compte peut compter dans plusieurs pays.",
    ov_none: "Aucune donnée de compte lisible.",
    kv_fi: "Institution déclarante", kv_id: "Numéro AFC", kv_year: "Année de déclaration", kv_type: "Type de déclaration", kv_balances: "Soldes (total)", kv_flags: "Particularités",
    type_CRS701: "Nouvelle déclaration (CRS701)", type_CRS702: "Déclaration de correction (CRS702)", type_CRS703: "Déclaration néant (CRS703)",
    flag_closed: "{n} clôturés", flag_undocumented: "{n} non documentés", flag_dormant: "{n} dormants", flag_joint: "{n} comptes joints", flag_none: "aucune",
    leg_individual: "personnes physiques", leg_CRS101: "ENF passive avec personnes détenant le contrôle (CRS101)", leg_CRS102: "entités devant faire l'objet d'une déclaration (CRS102)", leg_CRS103: "ENF passive elle-même déclarable (CRS103)",
    findings_title: "Constatations",
    no_findings: "Aucune constatation. Le fichier passe toutes les vérifications possibles avant le portail.",
    f_all: "Toutes", f_error: "Erreurs", f_input: "Saisie", f_info: "Remarques",
    loc_file: "Fichier", loc_header: "En-tête", loc_fi: "Institution déclarante", loc_account: "Compte {ref}", loc_cp: "personne détenant le contrôle {n}", loc_workbook: "Modèle", loc_sheet: "Feuille {sheet}", loc_row: "Ligne {row}",
    fix_label: "Que faire", official_label: "Texte de l'AFC (allemand)", technical_label: "Message technique",
    how_title: "Comment ça marche",
    how1_t: "Charger", how1: "Le navigateur charge une seule fois un environnement Python (Pyodide) et le paquet de vérification. Ensuite tout vient du cache.",
    how2_t: "Vérifier", how2: "Le fichier est lu dans la mémoire du navigateur : schéma OCDE, règles d'en-tête et de DocSpec, jeu de caractères, États partenaires de l'année, IBAN/ISIN, références croisées 3.0.",
    how3_t: "Corriger", how3: "Chaque constatation nomme le code AFC, l'endroit et ce qu'il faut faire. Seuls transport, déchiffrement, antivirus et enregistrement sont vérifiés par le portail seul.",
    privacy_title: "Protection des données en détail",
    privacy_html: "<strong>Votre fichier ne quitte pas le navigateur.</strong> Cette page est statique, sans analytique et sans composant serveur propre. Au chargement, seule cette page est contactée - l'environnement, les bibliothèques et le paquet de vérification sont sur le même serveur, et l'hébergeur voit la consultation comme pour n'importe quel site. Après la première visite, la page fonctionne aussi hors ligne. Après le choix du fichier, aucune requête réseau n'a lieu - une Content-Security-Policy de la page interdit au navigateur de contacter toute autre adresse. La langue, le thème et l'accès à votre registre sont mémorisés localement par le navigateur.",
    source: "Source et règles :", repo: "Repository aeoi", version: "Version",
    guidance: "Directive technique EAR de l'AFC, septembre 2026",
    english_note: "Messages techniques en anglais, avec le code d'erreur de l'AFC",
    theme: "Thème : {mode}", theme_auto: "automatique", theme_light: "clair", theme_dark: "sombre",
    report_name: "aeoi-rapport",
  },
  it: {
    title: "aeoi - Verificare un file CRS",
    tagline: "Verifica CRS nel browser",
    h1: "Verificare un file CRS, senza installare nulla",
    lead: "Schema 2.0 o 3.0, le regole della Direttiva tecnica SAI dell'AFC, set di caratteri, Stati partner, IBAN/ISIN - verificati nel suo browser. Il file non lo lascia.",
    badge_rules: "59 delle 65 regole dell'AFC",
    badge_local: "Nessun file lascia il browser",
    badge_open: "Open source, Apache-2.0",
    boot_title: "Ambiente di verifica",
    step1: "Ambiente", step2: "Librerie", step3: "Regole", step4: "Pronto",
    loading: "Caricamento dell'ambiente … (una sola volta, circa 20-40 MB, poi dalla cache del browser)",
    libs: "Caricamento delle librerie …",
    rules: "Caricamento delle regole …",
    ready: "Pronto. Da adesso non avviene più nessuna richiesta di rete.",
    boot_error: "Impossibile caricare l'ambiente: ",
    input_title: "Verificare un file",
    drop_title: "Trascini qui il file o clicchi",
    drop_hint: "CRS-XML (.xml) o modello Excel aeoi compilato (.xlsx) - lo schema 2.0 o 3.0 viene riconosciuto",
    version_label: "Versione dello schema per i modelli Excel",
    v3: "3.0 (dal 16.01.2027)", v2: "2.0 (fino al 14.12.2026)",
    mode_label: "Il file XML è una",
    mode_auto: "automatico (nome Test… = comunicazione test)", mode_test: "comunicazione test", mode_prod: "comunicazione produttiva",
    samples_label: "Provare senza un proprio file:",
    sample_ok: "Esempio (valido)", sample_bad: "Esempio (con errori)", sample_xlsx: "Modello di esempio (Excel)",
    running: "Verifica in corso …",
    check_error: "Errore durante la verifica: ",
    download: "Scaricare il rapporto", copy: "Copiare il rapporto", copied: "Copiato", again: "Verificare un altro file",
    verdict_ok: "Il file supera tutte le verifiche",
    verdict_bad: "Il portale respingerebbe questo file",
    verdict_unreadable: "Il file non ha potuto essere letto",
    sub_xml: "CRS-XML, schema {version} · verificato in {time}",
    sub_workbook: "Modello Excel aeoi, schema {version} · verificato in {time}",
    stat_errors: "Errori", stat_inputs: "Errori di inserimento", stat_notes: "Note", stat_accounts: "Conti", stat_persons: "persone fisiche", stat_entities: "enti", stat_cp: "persone che esercitano il controllo",
    ov_title: "Contenuto della comunicazione",
    ov_countries: "Residenza dei titolari di conto",
    ov_note: "Numero di conti per Paese di residenza del titolare; un conto può contare in più Paesi.",
    ov_none: "Nessun dato di conto leggibile.",
    kv_fi: "Istituto tenuto alla comunicazione", kv_id: "Numero AFC", kv_year: "Anno di comunicazione", kv_type: "Tipo di comunicazione", kv_balances: "Saldi (totale)", kv_flags: "Particolarità",
    type_CRS701: "Nuova comunicazione (CRS701)", type_CRS702: "Comunicazione di correzione (CRS702)", type_CRS703: "Comunicazione nulla (CRS703)",
    flag_closed: "{n} chiusi", flag_undocumented: "{n} non documentati", flag_dormant: "{n} dormienti", flag_joint: "{n} conti cointestati", flag_none: "nessuna",
    leg_individual: "persone fisiche", leg_CRS101: "NFE passiva con persone che esercitano il controllo (CRS101)", leg_CRS102: "enti oggetto di comunicazione (CRS102)", leg_CRS103: "NFE passiva essa stessa oggetto di comunicazione (CRS103)",
    findings_title: "Rilievi",
    no_findings: "Nessun rilievo. Il file supera tutte le verifiche possibili prima del portale.",
    f_all: "Tutti", f_error: "Errori", f_input: "Inserimento", f_info: "Note",
    loc_file: "File", loc_header: "Intestazione", loc_fi: "Istituto tenuto alla comunicazione", loc_account: "Conto {ref}", loc_cp: "persona che esercita il controllo {n}", loc_workbook: "Modello", loc_sheet: "Foglio {sheet}", loc_row: "Riga {row}",
    fix_label: "Cosa fare", official_label: "Testo dell'AFC (tedesco)", technical_label: "Messaggio tecnico",
    how_title: "Come funziona",
    how1_t: "Caricare", how1: "Il browser carica una sola volta un ambiente Python (Pyodide) e il pacchetto di verifica. Poi tutto arriva dalla cache.",
    how2_t: "Verificare", how2: "Il file viene letto nella memoria del browser: schema OCSE, regole di intestazione e DocSpec, set di caratteri, Stati partner dell'anno, IBAN/ISIN, riferimenti incrociati 3.0.",
    how3_t: "Correggere", how3: "Ogni rilievo indica il codice AFC, il punto e cosa fare. Solo trasporto, decifratura, antivirus e registrazione li verifica il portale da solo.",
    privacy_title: "Protezione dei dati in dettaglio",
    privacy_html: "<strong>Il file non lascia il browser.</strong> Questa pagina è statica, senza analytics e senza componente server propria. Al caricamento viene contattata solo questa pagina - ambiente, librerie e pacchetto di verifica sono sullo stesso server, e l'host vede la visita come per qualsiasi sito web. Dopo la prima visita la pagina funziona anche offline. Dopo la scelta del file non avviene nessuna richiesta di rete: una Content-Security-Policy della pagina impedisce al browser di contattare qualsiasi altro indirizzo. Lingua, tema e l'accesso al suo registro vengono ricordati localmente dal browser.",
    source: "Sorgente e regole:", repo: "Repository aeoi", version: "Versione",
    guidance: "Direttiva tecnica SAI dell'AFC, settembre 2026",
    english_note: "Messaggi tecnici in inglese, con il codice di errore dell'AFC",
    theme: "Tema: {mode}", theme_auto: "automatico", theme_light: "chiaro", theme_dark: "scuro",
    report_name: "aeoi-rapporto",
  },
};

let LANG = "de";

function t(key, vars) {
  let s = (I18N[LANG] && I18N[LANG][key]) || I18N.de[key] || key;
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.replace("{" + k + "}", v);
  return s;
}

// Re-renders every element with data-i18n; elements whose key changes at runtime (status)
// carry the current key in that attribute, so a language switch keeps their state.
function applyLanguage(lang) {
  LANG = I18N[lang] ? lang : "de";
  document.documentElement.lang = LANG;
  document.title = t("title");
  for (const el of document.querySelectorAll("[data-i18n]")) {
    const key = el.dataset.i18n;
    if (key.endsWith("_html")) el.innerHTML = t(key);
    else el.textContent = t(key);
  }
  document.getElementById("lang").value = LANG;
  try { localStorage.setItem("aeoi-lang", LANG); } catch (e) { /* private window or storage blocked */ }
  document.dispatchEvent(new CustomEvent("aeoi:language", { detail: LANG }));
}

function initialLanguage() {
  try {
    const saved = localStorage.getItem("aeoi-lang");
    if (saved && I18N[saved]) return saved;
  } catch (e) { /* ignore */ }
  const nav = (navigator.language || "de").slice(0, 2).toLowerCase();
  return I18N[nav] ? nav : "de";
}

document.getElementById("lang").addEventListener("change", (ev) => applyLanguage(ev.target.value));
// applyLanguage(initialLanguage()) is called by app.js once every dictionary file is loaded
