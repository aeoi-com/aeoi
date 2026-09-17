// Page texts in German, French and Italian. Own static strings only; "privacy_html" is the one
// key rendered as HTML (it carries <code> tags). The check results themselves come from the
// Python package and are in English, with the ESTV error code.
"use strict";

const I18N = {
  de: {
    title: "aeoi - CRS-Datei prüfen",
    h1: "aeoi - CRS-Datei prüfen, ohne etwas zu installieren",
    intro: "Prüft eine CRS-XML-Datei (Schema 2.0 oder 3.0) oder eine ausgefüllte aeoi-Excel-Vorlage nach dem OECD-Schema und nach den Regeln der Technischen Wegleitung AIA der ESTV (59 von 65; die übrigen - Transport, Entschlüsselung, Virenscan, Registrierung des Instituts - prüft nur das Portal). Zeichensatz, Partnerstaaten des Meldejahrs, IBAN/ISIN-Prüfsummen und die Querbezüge der 3.0-Elemente sind dabei.",
    privacy_html: "<strong>Datenschutz:</strong> Ihre Datei verlässt den Browser nicht; die Prüfung läuft in Ihrem Browser. Diese Seite ist statisch, ohne Analytics und ohne eigene Serverkomponente. Beim Laden werden nur <code>cdn.jsdelivr.net</code> (Pyodide), <code>pypi.org</code> und <code>files.pythonhosted.org</code> (Bibliotheken) angefragt; der Host der Seite sieht den Seitenaufruf wie jede Website. Nach der Dateiauswahl findet keine Netzanfrage mehr statt - eine Content-Security-Policy der Seite lässt den Browser keine andere Adresse kontaktieren.",
    loading: "Laufzeit wird geladen … (einmalig etwa 20-40 MB, danach aus dem Browser-Cache)",
    libs: "Bibliotheken werden geladen …",
    ready: "Bereit. Ab jetzt findet keine Netzanfrage mehr statt.",
    boot_error: "Die Laufzeit konnte nicht geladen werden: ",
    options: "Optionen",
    version_label: "Schema-Version für Excel-Vorlagen:",
    v3: "3.0 (ab 16.01.2027)",
    v2: "2.0 (bis 14.12.2026)",
    mode_label: "XML-Datei ist eine",
    mode_auto: "… aus dem Dateinamen erkennen (Test… = Testmeldung)",
    mode_test: "Testmeldung",
    mode_prod: "produktive Meldung",
    choose: "Datei wählen",
    xml_label: "CRS-XML-Datei:",
    xlsx_label: "aeoi-Excel-Vorlage:",
    none_yet: "Noch keine Datei geprüft.",
    running: "Prüfung läuft …",
    check_error: "Fehler bei der Prüfung: ",
    source: "Quelle und Regeln:",
    repo: "Repository aeoi",
    version: "Version",
    guidance: "Technische Wegleitung AIA der ESTV, September 2026. Die Prüfmeldungen erscheinen auf Englisch, mit dem Fehlercode der ESTV.",
  },
  fr: {
    title: "aeoi - Vérifier un fichier CRS",
    h1: "aeoi - Vérifier un fichier CRS, sans rien installer",
    intro: "Vérifie un fichier CRS-XML (schéma 2.0 ou 3.0) ou un modèle Excel aeoi rempli, selon le schéma de l'OCDE et selon les règles de la Directive technique EAR de l'AFC (59 sur 65 ; les autres - transport, déchiffrement, antivirus, enregistrement de l'institution - ne sont vérifiées que par le portail). Jeu de caractères, États partenaires de l'année de déclaration, clés de contrôle IBAN/ISIN et références croisées des éléments 3.0 compris.",
    privacy_html: "<strong>Protection des données :</strong> votre fichier ne quitte pas le navigateur ; la vérification s'exécute dans votre navigateur. Cette page est statique, sans analytique et sans composant serveur propre. Au chargement, seuls <code>cdn.jsdelivr.net</code> (Pyodide), <code>pypi.org</code> et <code>files.pythonhosted.org</code> (bibliothèques) sont contactés ; l'hébergeur de la page voit la consultation comme n'importe quel site. Après le choix du fichier, plus aucune requête réseau n'a lieu - une Content-Security-Policy de la page interdit au navigateur de contacter toute autre adresse.",
    loading: "Chargement de l'environnement … (une seule fois, environ 20-40 Mo, ensuite depuis le cache du navigateur)",
    libs: "Chargement des bibliothèques …",
    ready: "Prêt. À partir de maintenant, plus aucune requête réseau.",
    boot_error: "L'environnement n'a pas pu être chargé : ",
    options: "Options",
    version_label: "Version du schéma pour les modèles Excel :",
    v3: "3.0 (dès le 16.01.2027)",
    v2: "2.0 (jusqu'au 14.12.2026)",
    mode_label: "Le fichier XML est une",
    mode_auto: "… détection d'après le nom du fichier (Test… = déclaration test)",
    mode_test: "déclaration test",
    mode_prod: "déclaration productive",
    choose: "Choisir un fichier",
    xml_label: "Fichier CRS-XML :",
    xlsx_label: "Modèle Excel aeoi :",
    none_yet: "Aucun fichier vérifié pour l'instant.",
    running: "Vérification en cours …",
    check_error: "Erreur lors de la vérification : ",
    source: "Source et règles :",
    repo: "Repository aeoi",
    version: "Version",
    guidance: "Directive technique EAR de l'AFC, septembre 2026. Les messages de vérification sont en anglais, avec le code d'erreur de l'AFC.",
  },
  it: {
    title: "aeoi - Verificare un file CRS",
    h1: "aeoi - Verificare un file CRS, senza installare nulla",
    intro: "Verifica un file CRS-XML (schema 2.0 o 3.0) o un modello Excel aeoi compilato, secondo lo schema OCSE e secondo le regole della Direttiva tecnica SAI dell'AFC (59 su 65; le altre - trasporto, decifratura, antivirus, registrazione dell'istituto - le verifica solo il portale). Set di caratteri, Stati partner dell'anno di comunicazione, cifre di controllo IBAN/ISIN e riferimenti incrociati degli elementi 3.0 inclusi.",
    privacy_html: "<strong>Protezione dei dati:</strong> il file non lascia il browser; la verifica avviene nel suo browser. Questa pagina è statica, senza analytics e senza componente server propria. Al caricamento vengono contattati solo <code>cdn.jsdelivr.net</code> (Pyodide), <code>pypi.org</code> e <code>files.pythonhosted.org</code> (librerie); l'host della pagina vede la visita come qualsiasi sito web. Dopo la scelta del file non avviene più nessuna richiesta di rete: una Content-Security-Policy della pagina impedisce al browser di contattare qualsiasi altro indirizzo.",
    loading: "Caricamento dell'ambiente … (una sola volta, circa 20-40 MB, poi dalla cache del browser)",
    libs: "Caricamento delle librerie …",
    ready: "Pronto. Da adesso non avviene più nessuna richiesta di rete.",
    boot_error: "Impossibile caricare l'ambiente: ",
    options: "Opzioni",
    version_label: "Versione dello schema per i modelli Excel:",
    v3: "3.0 (dal 16.01.2027)",
    v2: "2.0 (fino al 14.12.2026)",
    mode_label: "Il file XML è una",
    mode_auto: "… riconoscimento dal nome del file (Test… = comunicazione test)",
    mode_test: "comunicazione test",
    mode_prod: "comunicazione produttiva",
    choose: "Scegliere il file",
    xml_label: "File CRS-XML:",
    xlsx_label: "Modello Excel aeoi:",
    none_yet: "Nessun file ancora verificato.",
    running: "Verifica in corso …",
    check_error: "Errore durante la verifica: ",
    source: "Sorgente e regole:",
    repo: "Repository aeoi",
    version: "Versione",
    guidance: "Direttiva tecnica SAI dell'AFC, settembre 2026. I messaggi di verifica sono in inglese, con il codice di errore dell'AFC.",
  },
};

let LANG = "de";

function t(key) {
  return (I18N[LANG] && I18N[LANG][key]) || I18N.de[key] || key;
}

// Re-renders every element with data-i18n; elements whose key changes at runtime (status, out)
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
applyLanguage(initialLanguage());
