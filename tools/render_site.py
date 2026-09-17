"""Render the marketing pages of meldbar.ch into web/ from shared fragments (header, footer) and
per-page bodies. Texts come from web/site-i18n.js at runtime (data-i18n); the German text in the
HTML is the no-JS fallback.

    python tools/render_site.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"

CSP = (
    "default-src 'self'; script-src 'self'; connect-src 'self'; style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; font-src 'self'; manifest-src 'self'; object-src 'none'; base-uri 'none'; "
    "form-action 'self'"
)

MARK = (
    '<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M30 5h29q4 0 1.6 3.2l-7.2 10.6Q51 22 47 22H18q-4 0-1.6-3.2l7.2-10.6Q26 5 30 5Z" fill="#1c4f9e"/>'
    '<path d="M25 21h29q4 0 1.6 3.2l-7.2 10.6Q46 38 42 38H13q-4 0-1.6-3.2l7.2-10.6Q21 21 25 21Z" fill="#2b86c9"/>'
    '<path d="M20 37h29q4 0 1.6 3.2l-7.2 10.6Q41 54 37 54H8q-4 0-1.6-3.2l7.2-10.6Q16 37 20 37Z" fill="#13a89e"/></svg>'
)
CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7"/></svg>'

NAV = [
    ("index.html#funktionen", "nav_features", "Funktionen"),
    ("index.html#ablauf", "nav_how", "So funktioniert es"),
    ("preise.html", "nav_pricing", "Preise"),
    ("ueber-uns.html", "nav_about", "Über uns"),
    ("kontakt.html", "nav_contact", "Kontakt"),
]


def header(page: str) -> str:
    links = ""
    for href, key, de in NAV:
        active = ' class="active"' if href == page else ""
        links += f'<a href="{href}" data-i18n="{key}"{active}>{de}</a>'
    mobile = "".join(f'<a href="{href}" data-i18n="{key}">{de}</a>' for href, key, de in NAV)
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="logo" href="index.html">{MARK}<span>meldbar</span></a>
    <nav class="site-nav" aria-label="Hauptnavigation">{links}</nav>
    <div class="header-actions">
      <label class="sr-only" for="lang">Sprache / Langue / Lingua</label>
      <select id="lang" class="pill lang"><option value="de">Deutsch</option><option value="fr">Français</option><option value="it">Italiano</option></select>
      <a class="btn primary" href="app.html" data-i18n="nav_app">App öffnen</a>
      <button class="burger" type="button" aria-expanded="false" aria-controls="mobile-nav"><span class="sr-only" data-i18n="nav_menu">Menü</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    </div>
  </div>
  <nav class="mobile-nav" id="mobile-nav" aria-label="Navigation">{mobile}<a class="btn primary" href="app.html" data-i18n="nav_app">App öffnen</a></nav>
</header>"""


FOOTER = f"""<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <div class="foot-brand">{MARK}<span>meldbar</span></div>
        <p data-i18n="foot_note">Ihre Daten bleiben in Ihrem Browser. Keine Analytics, keine Cookies, kein Server.</p>
        <p data-i18n="foot_address">meldbar · Salvatorstrasse 8 · 8050 Zürich · Schweiz</p>
      </div>
      <div>
        <h4 data-i18n="foot_product">Produkt</h4>
        <ul>
          <li><a href="app.html" data-i18n="foot_app">Web-App</a></li>
          <li><a href="preise.html" data-i18n="foot_pricing">Preise</a></li>
          <li><a href="https://github.com/aeoi-com/aeoi/blob/main/docs/de/ANLEITUNG.md" data-i18n="foot_docs">Anleitung</a></li>
          <li><a href="https://github.com/aeoi-com/aeoi/blob/main/CHANGELOG.md" data-i18n="foot_changes">Änderungen</a></li>
        </ul>
      </div>
      <div>
        <h4 data-i18n="foot_company">Unternehmen</h4>
        <ul>
          <li><a href="ueber-uns.html" data-i18n="foot_about">Über uns</a></li>
          <li><a href="kontakt.html" data-i18n="foot_contact">Kontakt</a></li>
          <li><a href="https://github.com/aeoi-com/aeoi" data-i18n="foot_source">Quellcode (GitHub)</a></li>
        </ul>
      </div>
      <div>
        <h4 data-i18n="foot_legal">Rechtliches</h4>
        <ul>
          <li><a href="impressum.html" data-i18n="foot_imprint">Impressum</a></li>
          <li><a href="datenschutz.html" data-i18n="foot_privacy">Datenschutz</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span data-i18n="foot_rights">© 2026 meldbar. Alle Rechte vorbehalten.</span>
      <span>Salvatorstrasse 8, 8050 Zürich</span>
    </div>
  </div>
</footer>"""


def page(name: str, title: str, body: str, *, desc: str) -> str:
    return f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="no-referrer">
<meta name="color-scheme" content="light">
<meta name="description" content="{desc}">
<title>{title}</title>
<link rel="stylesheet" href="styles.css">
<link rel="stylesheet" href="site.css">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#1c4f9e">
<link rel="icon" href="logo-mark.svg" type="image/svg+xml">
</head>
<body data-page="{name}">
<div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
{header(name + ".html" if name != "home" else "index.html")}
<main>
{body}
</main>
{FOOTER}
<script src="site-i18n.js"></script>
<script src="site.js"></script>
</body>
</html>
'''


def feature(i: int, icon: str, title: str, text: str) -> str:
    return f"""      <div class="feature reveal d{i % 3 + 1}">
        <div class="ico">{icon}</div>
        <h3 data-i18n="f{i}_t">{title}</h3>
        <p data-i18n="f{i}_p">{text}</p>
      </div>"""


ICONS = {
    1: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="9"/></svg>',
    2: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16M4 12h16M4 18h10"/><path d="M18 15l3 3-3 3"/></svg>',
    3: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>',
    4: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/></svg>',
    5: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v10H8l-4 4z"/><path d="M9 10h6"/></svg>',
    6: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/></svg>',
}

STEP_ART = {
    1: '<svg viewBox="0 0 200 56"><rect x="4" y="6" width="120" height="44" rx="6" fill="var(--surface-2)" stroke="var(--border-strong)"/><rect x="12" y="14" width="40" height="6" rx="3" fill="var(--warn)"/><rect x="58" y="14" width="30" height="6" rx="3" fill="var(--border-strong)"/><rect x="12" y="26" width="104" height="5" rx="2.5" fill="var(--border)"/><rect x="12" y="36" width="104" height="5" rx="2.5" fill="var(--border)"/><path d="M150 28l30 0M172 18l10 10-10 10" fill="none" stroke="var(--accent-2)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    2: '<svg viewBox="0 0 200 56"><rect x="4" y="6" width="192" height="44" rx="6" fill="var(--surface-2)" stroke="var(--border-strong)"/><rect x="12" y="14" width="60" height="6" rx="3" fill="var(--warn)"/><rect x="80" y="14" width="40" height="6" rx="3" fill="var(--warn)"/><rect x="128" y="14" width="40" height="6" rx="3" fill="var(--border-strong)"/><rect x="12" y="28" width="60" height="5" rx="2.5" fill="var(--accent-2)"/><rect x="80" y="28" width="40" height="5" rx="2.5" fill="var(--accent-2)"/><rect x="128" y="28" width="40" height="5" rx="2.5" fill="var(--accent-2)"/><rect x="12" y="39" width="60" height="5" rx="2.5" fill="var(--border)"/><rect x="80" y="39" width="40" height="5" rx="2.5" fill="var(--border)"/></svg>',
    3: '<svg viewBox="0 0 200 56"><rect x="4" y="6" width="192" height="44" rx="6" fill="var(--ok-soft)" stroke="var(--ok)"/><circle cx="26" cy="28" r="10" fill="var(--ok)"/><path d="M20 28l4 4 8-8" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><rect x="46" y="20" width="90" height="6" rx="3" fill="var(--ok)"/><rect x="46" y="32" width="60" height="5" rx="2.5" fill="color-mix(in srgb, var(--ok) 50%, transparent)"/></svg>',
    4: '<svg viewBox="0 0 200 56"><rect x="30" y="8" width="60" height="40" rx="5" fill="var(--surface-2)" stroke="var(--border-strong)"/><text x="60" y="33" text-anchor="middle" font-size="11" font-weight="600" fill="var(--muted)" font-family="Inter,system-ui">XML</text><path d="M96 28h22" stroke="var(--accent-2)" stroke-width="2.5" stroke-linecap="round"/><rect x="124" y="8" width="52" height="40" rx="5" fill="var(--accent)"/><rect x="141" y="24" width="18" height="14" rx="3" fill="#fff"/><path d="M144 24v-4a6 6 0 0 1 12 0v4" fill="none" stroke="#fff" stroke-width="2.5"/></svg>',
    5: '<svg viewBox="0 0 200 56"><rect x="4" y="6" width="120" height="44" rx="6" fill="var(--surface-2)" stroke="var(--border-strong)"/><path d="M64 40V16M52 26l12-12 12 12" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="162" cy="28" r="16" fill="var(--ok-soft)" stroke="var(--ok)"/><path d="M154 28l6 6 10-11" fill="none" stroke="var(--ok)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}

STEPS_DATA = [
    (
        1,
        "Vorlage herunterladen",
        "Die Excel-Vorlage aus der App: ein Blatt für das Institut, eines für die Konten, eines für beherrschende Personen, eines für Zahlungen.",
    ),
    (
        2,
        "Ausfüllen",
        "In Ihrem Excel, wie gewohnt. Gelbe Spalten sind Pflicht, Listen zeigen die erlaubten Codes, jede Spalte erklärt sich per Kommentar.",
    ),
    (
        3,
        "Prüfen",
        "Datei in die App ziehen. Sekunden später: grün, oder eine Liste mit Befunden - Konto, Feld, ESTV-Code, was zu tun ist.",
    ),
    (
        4,
        "Erstellen und verschlüsseln",
        "Register öffnen, Schlüssel der ESTV einmal wählen, «Erstellen». Das Paket ist bereit für das AIA-Portal.",
    ),
    (
        5,
        "Hochladen und Ergebnis erfassen",
        "Im Portal hochladen wie bisher. Die Bestätigung in die App einfügen - damit sind die Korrekturen des nächsten Jahres vorbereitet.",
    ),
]
STEP_LINK = {  # step 1: the static template, served in the language of the page (site.js sets href)
    1: '<p class="step-link"><a href="vorlage/meldbar-vorlage-de.xlsx" data-vorlage download data-i18n="s1_dl">Excel-Vorlage herunterladen</a></p>',
}
STEPS = "".join(
    f'<div class="step-card"><div class="n">{i}</div><h3 data-i18n="s{i}_t">{title}</h3>'
    f'<p data-i18n="s{i}_p">{text}</p>{STEP_LINK.get(i, "")}<div class="art">{STEP_ART[i]}</div></div>'
    for i, title, text in STEPS_DATA
)

HOME = f"""
<section class="hero-section">
  <div class="wrap hero-grid">
    <div>
      <span class="hero-kicker"><i class="pulse"></i><span data-i18n="hero_kicker">Ab 16. Januar 2027 nur noch CRS-Schema 3.0</span></span>
      <h1 class="hero-h1" data-i18n="hero_h1">CRS-Meldungen. Geprüft, verschlüsselt, bereit zum Hochladen.</h1>
      <p class="hero-lead" data-i18n="hero_lead">meldbar macht aus Ihrer Excel-Tabelle die fertige AIA-Meldung für das Portal der ESTV - und prüft sie vorher wie das Portal. Im Browser, ohne Installation. Ihre Kontodaten verlassen Ihren Rechner nicht.</p>
      <div class="hero-actions">
        <a class="btn primary lg" href="app.html" data-i18n="hero_cta">Jetzt Datei prüfen</a>
        <a class="btn lg ghost" href="#ablauf" data-i18n="hero_cta2">So funktioniert es</a>
      </div>
      <div class="trust">
        <span>{CHECK}<span data-i18n="hero_trust1">59 von 65 ESTV-Regeln</span></span>
        <span>{CHECK}<span data-i18n="hero_trust2">Keine Datei verlässt den Browser</span></span>
        <span>{CHECK}<span data-i18n="hero_trust3">Deutsch · Français · Italiano</span></span>
      </div>
    </div>
    <div class="illu" aria-hidden="true">
      <svg viewBox="8 62 516 304">
        <path class="flow" d="M150 128 C 230 128, 230 208, 300 208"/>
        <path class="flow" d="M150 300 C 230 300, 230 208, 300 208"/>
        <path class="flow" d="M410 208 C 440 208, 440 208, 470 208"/>
        <g class="float1">
          <rect class="card-f" x="20" y="76" width="130" height="104" rx="12"/>
          <text class="lbl" x="36" y="102" data-i18n="ill_excel">Excel</text>
          <rect class="row y" x="36" y="116" width="98" height="8" rx="4"/><rect class="row" x="36" y="132" width="98" height="8" rx="4"/><rect class="row" x="36" y="148" width="70" height="8" rx="4"/>
        </g>
        <g class="float2">
          <rect class="card-f" x="20" y="248" width="130" height="104" rx="12"/>
          <text class="lbl" x="36" y="274" data-i18n="ill_check">Prüfung</text>
          <rect class="row g" x="36" y="288" width="98" height="8" rx="4"/><rect class="row g" x="36" y="304" width="98" height="8" rx="4"/><rect class="row g" x="36" y="320" width="70" height="8" rx="4"/>
        </g>
        <g class="float3">
          <rect class="card-f" x="300" y="156" width="110" height="104" rx="12"/>
          <text class="lbl" x="316" y="182" data-i18n="ill_xml">CRS-XML</text>
          <text class="sub" x="316" y="200">&lt;crs:CRS_OECD&gt;</text>
          <rect class="row" x="316" y="212" width="78" height="8" rx="4"/><rect class="row" x="316" y="228" width="60" height="8" rx="4"/>
        </g>
        <g class="float1">
          <rect class="lock" x="470" y="176" width="48" height="64" rx="12"/>
          <rect x="484" y="204" width="20" height="16" rx="3" fill="#fff"/>
          <path d="M487 204v-6a7 7 0 0 1 14 0v6" fill="none" stroke="#fff" stroke-width="3"/>
        </g>
        <circle cx="150" cy="128" r="14" fill="var(--ok)"/>
        <path class="tick" d="M143 128l5 5 9-10"/>
        <circle cx="150" cy="300" r="14" fill="var(--ok)"/>
        <path class="tick" d="M143 300l5 5 9-10"/>
      </svg>
    </div>
  </div>
</section>

<section class="section tight" id="frist">
  <div class="wrap">
    <div class="deadline reveal">
      <span class="kicker" data-i18n="deadline_kicker">Was seit dem 1. Januar gilt</span>
      <h2 class="h2" data-i18n="deadline_h2">Der revidierte CRS ist in Kraft - und das Portal wechselt das Schema.</h2>
      <p data-i18n="deadline_p">Seit dem 1. Januar 2026 gilt in der Schweiz der revidierte gemeinsame Meldestandard. Die ESTV nimmt bis zum 14. Dezember 2026 nur das Schema 2.0 an, ab dem 16. Januar 2027 nur noch das Schema 3.0. Die Meldungen für das Jahr 2026 - Frist 30. Juni 2027 - sind die ersten, die im neuen Format erstellt werden müssen.</p>
      <div class="countdown">
        <div class="cd"><div class="n" data-until="2027-01-16">-</div><div class="l" data-i18n="cd_switch">Tage bis zum Schemawechsel (16.01.2027)</div></div>
        <div class="cd"><div class="n" data-until="2027-06-30">-</div><div class="l" data-i18n="cd_deadline">Tage bis zur Frist (30.06.2027)</div></div>
      </div>
      <p class="src" data-i18n="deadline_src">Quelle: Technische Wegleitung AIA der ESTV, September 2026, Ziffer 5.3.1; Art. 15 Abs. 1 AIAG.</p>
    </div>
  </div>
</section>

<section class="section" id="funktionen">
  <div class="wrap">
    <span class="kicker reveal" data-i18n="features_kicker">Funktionen</span>
    <h2 class="h2 reveal" data-i18n="features_h2">Alles, was zwischen Ihrer Tabelle und dem Portal liegt.</h2>
    <div class="features">
{feature(1, ICONS[1], "Prüfen wie das Portal", "OECD-Schema 2.0 und 3.0, 59 von 65 Regeln der Technischen Wegleitung, Zeichensatz, Partnerstaaten des Berichtsjahrs, IBAN/ISIN - jeder Befund mit ESTV-Code, Stelle und Abhilfe, auf Deutsch.")}
{feature(2, ICONS[2], "Excel rein, XML raus", "Eine Vorlage mit vier Blättern, Drop-down-Listen und Hinweisen. Ein Klick erstellt die CRS-XML-Datei mit allen Kennungen.")}
{feature(3, ICONS[3], "Verschlüsselt für die ESTV", "Das Paket entsteht genau nach Ziffer 3.3.1 der Wegleitung - AES-256, öffentlicher Schlüssel der ESTV, richtiger Dateiname für Test und Produktion.")}
{feature(4, ICONS[4], "Korrekturen ohne Kopfzerbrechen", "Das Register merkt sich, was gesendet wurde. Im nächsten Jahr dieselbe Tabelle anpassen: geänderte Konten werden Korrekturen, gestrichene Storni, neue eine Neumeldung.")}
{feature(5, ICONS[5], "Ergebnis des Portals verstehen", "Validierungsbestätigung einfügen - jeder Code wird erklärt, das Register weiss, ob die Meldung angenommen wurde.")}
{feature(6, ICONS[6], "Ihre Daten bleiben bei Ihnen", "Kein Server, keine Analytics, keine Cookies. Die Prüfung läuft in Ihrem Browser; eine Sicherheitsrichtlinie verbietet jede andere Verbindung. Nach dem ersten Besuch auch offline.")}
    </div>
    <div class="stats">
      <div class="stat-b reveal"><div class="n" data-count="59">0</div><div class="l" data-i18n="stat1_l">ESTV-Regeln geprüft, bevor das Portal sie sieht</div></div>
      <div class="stat-b reveal d1"><div class="n" data-count="0">0</div><div class="l" data-i18n="stat2_l">Server, die Ihre Kontodaten sehen</div></div>
      <div class="stat-b reveal d2"><div class="n" data-count="3">0</div><div class="l" data-i18n="stat3_l">Sprachen: Deutsch, Französisch, Italienisch</div></div>
      <div class="stat-b reveal d3"><div class="n" data-count="2">0</div><div class="l" data-i18n="stat4_l">Schemata: 2.0 bis 14.12.2026, 3.0 ab 16.01.2027</div></div>
    </div>
  </div>
</section>

<section class="section" id="ablauf">
  <div class="how-wrap">
    <div class="how-sticky">
      <div class="wrap">
        <span class="kicker reveal" data-i18n="how_kicker">So funktioniert es</span>
        <h2 class="h2 reveal" data-i18n="how_h2">Fünf Schritte. Kein Handbuch nötig.</h2>
        <p class="how-hint" data-i18n="how_hint">Weiterscrollen - die Schritte laufen nach rechts.</p>
        <div class="how-track">
          {STEPS}
        </div>
        <div class="how-progress"><i></i></div>
        <p style="margin-top:22px"><a class="btn primary" href="app.html" data-i18n="how_cta">Mit einer Datei ausprobieren</a></p>
      </div>
    </div>
  </div>
</section>

<section class="section" id="datenschutz">
  <div class="wrap privacy-grid">
    <div>
      <span class="kicker reveal" data-i18n="privacy_kicker">Datenschutz</span>
      <h2 class="h2 reveal" data-i18n="privacy_h2">Ihre Kontodaten verlassen Ihren Rechner nicht. Technisch garantiert, nicht nur versprochen.</h2>
      <p class="lead reveal d1" data-i18n="privacy_p">meldbar ist eine statische Webseite ohne Serverkomponente. Die gesamte Prüfung läuft in Ihrem Browser. Eine Content-Security-Policy verbietet dem Browser, nach dem Laden irgendeine andere Adresse zu kontaktieren.</p>
      <div class="checks reveal d2">
        <div>{CHECK}<span data-i18n="pv1">Keine Analytics, keine Cookies, keine Konten</span></div>
        <div>{CHECK}<span data-i18n="pv2">Quellcode offen (Apache-2.0), jede Regel nachlesbar</span></div>
        <div>{CHECK}<span data-i18n="pv3">Funktioniert nach dem ersten Besuch auch offline</span></div>
      </div>
    </div>
    <div class="diagram reveal d2" aria-hidden="true">
      <svg viewBox="0 0 520 300">
        <rect class="box" x="20" y="40" width="240" height="220" rx="16"/>
        <text class="t" x="40" y="70" data-i18n="diag_browser">Ihr Browser</text>
        <rect class="file" x="60" y="100" width="150" height="110" rx="10"/>
        <text class="t" x="78" y="130" data-i18n="diag_file">Ihre Datei</text>
        <rect x="78" y="146" width="112" height="8" rx="4" fill="var(--accent)" opacity="0.5"/><rect x="78" y="162" width="90" height="8" rx="4" fill="var(--accent)" opacity="0.35"/><rect x="78" y="178" width="100" height="8" rx="4" fill="var(--accent)" opacity="0.35"/>
        <g class="glow"><path class="shield" d="M228 96l16 6v12c0 10-7 16-16 18-9-2-16-8-16-18v-12z"/><path d="M222 114l4 4 8-8" fill="none" stroke="var(--ok)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g>
        <path class="link" d="M262 150 H 380"/>
        <path class="cross" d="M312 136l20 28M332 136l-20 28"/>
        <text class="s" x="322" y="180" text-anchor="middle" data-i18n="diag_no">keine Verbindung</text>
        <rect class="box" x="384" y="110" width="116" height="80" rx="14"/>
        <text class="t" x="442" y="155" text-anchor="middle" data-i18n="diag_internet">Internet</text>
      </svg>
    </div>
  </div>
</section>

<section class="section" id="preise">
  <div class="wrap center">
    <span class="kicker reveal" data-i18n="pricing_kicker">Preise</span>
    <h2 class="h2 reveal" data-i18n="pricing_h2">Kostenlos für alle. Abonnement für die, die Unterstützung wollen.</h2>
    <p class="lead reveal d1" data-i18n="pricing_p">Pro Organisation, nicht pro Benutzer. Meldende Institute unbegrenzt.</p>
    <div class="plans" style="text-align:left">
      <div class="plan-card reveal"><h3 data-i18n="pr_free">Basis</h3><div class="price" data-i18n="pr_free_price">0 CHF</div><div class="per" data-i18n="pr_free_per">für immer</div>
        <ul><li>{CHECK}<span data-i18n="pr_free_1">Web-App mit allen Prüfungen</span></li><li>{CHECK}<span data-i18n="pr_free_2">Excel-Vorlage, XML-Erstellung, Verschlüsselung</span></li><li>{CHECK}<span data-i18n="pr_free_3">Register für Korrekturen und Storni</span></li></ul>
        <a class="btn" href="app.html" data-i18n="pr_free_btn">App öffnen</a></div>
      <div class="plan-card featured reveal d1"><span class="badge-top" data-i18n="pr_popular">Empfohlen</span><h3 data-i18n="pr_pro">Pro</h3><div class="price" data-i18n="pr_pro_price">ab 900 CHF</div><div class="per" data-i18n="pr_pro_per">pro Jahr und Organisation</div>
        <ul><li>{CHECK}<span data-i18n="pr_pro_1">Alles aus Basis</span></li><li>{CHECK}<span data-i18n="pr_pro_2">Support mit Vorrang in der Meldesaison</span></li><li>{CHECK}<span data-i18n="pr_pro_3">Garantierte Aktualisierung bei neuen Regeln</span></li><li>{CHECK}<span data-i18n="pr_pro_4">Durchsicht der ersten Meldung</span></li></ul>
        <a class="btn primary" href="kontakt.html" data-i18n="pr_pro_btn">Angebot anfragen</a></div>
      <div class="plan-card reveal d2"><h3 data-i18n="pr_lib">Softwarehäuser</h3><div class="price" data-i18n="pr_lib_price">2'500 CHF</div><div class="per" data-i18n="pr_lib_per">pro Jahr</div>
        <ul><li>{CHECK}<span data-i18n="pr_lib_1">Python-Bibliothek in Ihrem Produkt</span></li><li>{CHECK}<span data-i18n="pr_lib_2">Technischer Support bei der Integration</span></li><li>{CHECK}<span data-i18n="pr_lib_3">Frühzeitige Information zu Änderungen</span></li></ul>
        <a class="btn" href="kontakt.html" data-i18n="pr_lib_btn">Kontakt aufnehmen</a></div>
    </div>
    <p style="margin-top:20px"><a href="preise.html" data-i18n="pricing_all">Alle Preise und Leistungen</a></p>
  </div>
</section>

<section class="section tight">
  <div class="wrap">
    <div class="cta-band reveal">
      <h2 class="h2" data-i18n="cta_h2">Bereit für das Schema 3.0?</h2>
      <p data-i18n="cta_p">Öffnen Sie die App und prüfen Sie Ihre erste Datei. Ohne Konto, ohne Installation.</p>
      <a class="btn primary lg" href="app.html" data-i18n="cta_btn">App öffnen</a>
    </div>
  </div>
</section>
"""


def plan_li(keys: list[str], fallback: list[str]) -> str:
    return "".join(
        f'<li>{CHECK}<span data-i18n="{k}">{f}</span></li>' for k, f in zip(keys, fallback)
    )


PRICING = f"""
<section class="section">
  <div class="wrap">
    <span class="kicker" data-i18n="pricing_kicker">Preise</span>
    <h1 class="h2" data-i18n="pr_h1">Preise</h1>
    <p class="lead" data-i18n="pr_lead">Das Werkzeug ist und bleibt kostenlos - der Quellcode ist offen. Wer Sicherheit in der Meldesaison will, wählt ein Abonnement pro Organisation: eine Rechnung, beliebig viele meldende Institute, beliebig viele Benutzer.</p>
    <div class="plans">
      <div class="plan-card reveal"><h3 data-i18n="pr_free">Basis</h3><div class="price" data-i18n="pr_free_price">0 CHF</div><div class="per" data-i18n="pr_free_per">für immer</div>
        <ul>{plan_li(["pr_free_1", "pr_free_2", "pr_free_3", "pr_free_4", "pr_free_5"], ["Web-App mit allen Prüfungen (59 von 65 ESTV-Regeln)", "Excel-Vorlage, XML-Erstellung, Verschlüsselung", "Register für Korrekturen und Storni", "Deutsch, Französisch, Italienisch", "Hilfe über das öffentliche Repository"])}</ul>
        <a class="btn" href="app.html" data-i18n="pr_free_btn">App öffnen</a></div>
      <div class="plan-card featured reveal d1"><span class="badge-top" data-i18n="pr_popular">Empfohlen</span><h3 data-i18n="pr_pro">Pro</h3><div class="price" data-i18n="pr_pro_price">ab 900 CHF</div><div class="per" data-i18n="pr_pro_per">pro Jahr und Organisation</div>
        <ul>{plan_li(["pr_pro_1", "pr_pro_2", "pr_pro_3", "pr_pro_4", "pr_pro_5"], ["Alles aus Basis", "Support per E-Mail, mit Vorrang in der Meldesaison (Mai-Juni)", "Garantierte Aktualisierung bei neuen Regeln der ESTV oder der OECD", "Durchsicht der ersten Meldung vor dem Hochladen", "Einführung (1 Stunde, online) für Ihr Team"])}</ul>
        <div class="bands"><div><span data-i18n="pr_band1">1-10 Vehikel</span><b data-i18n="pr_band1_p">900 CHF / Jahr</b></div><div><span data-i18n="pr_band2">11-50 Vehikel</span><b data-i18n="pr_band2_p">1'500 CHF / Jahr</b></div><div><span data-i18n="pr_band3">über 50 Vehikel</span><b data-i18n="pr_band3_p">2'400 CHF / Jahr</b></div></div>
        <a class="btn primary" href="kontakt.html" data-i18n="pr_pro_btn" style="margin-top:18px">Angebot anfragen</a></div>
      <div class="plan-card reveal d2"><h3 data-i18n="pr_lib">Softwarehäuser</h3><div class="price" data-i18n="pr_lib_price">2'500 CHF</div><div class="per" data-i18n="pr_lib_per">pro Jahr</div>
        <ul>{plan_li(["pr_lib_1", "pr_lib_2", "pr_lib_3", "pr_lib_4"], ["Python-Bibliothek in Ihrem Produkt einsetzen", "Technischer Support bei der Integration", "Frühzeitige Information zu Schema- und Regeländerungen", "Nennung als Partner, wenn gewünscht"])}</ul>
        <a class="btn" href="kontakt.html" data-i18n="pr_lib_btn">Kontakt aufnehmen</a></div>
    </div>
    <div class="pilot reveal"><h3 data-i18n="pr_pilot_t">Pilotinstitute</h3><p data-i18n="pr_pilot_p">Ein bis drei Institute, die im November 2026 und im Januar 2027 Testmeldungen über das Portal senden, zahlen während des Pilotversuchs nichts und erhalten den vollen Pro-Support.</p></div>
    <h2 class="h2" style="margin-top:40px" data-i18n="pr_faq_t">Häufige Fragen</h2>
    <div class="faq">
      <details><summary data-i18n="pr_q1">Was zählt als Vehikel?</summary><p data-i18n="pr_a1">Jedes meldende Finanzinstitut, für das Sie Meldungen einreichen.</p></details>
      <details><summary data-i18n="pr_q2">Brauche ich das Abonnement, um die App zu nutzen?</summary><p data-i18n="pr_a2">Nein.</p></details>
      <details><summary data-i18n="pr_q3">Laden Sie die Meldung für uns hoch?</summary><p data-i18n="pr_a3">Nein.</p></details>
      <details><summary data-i18n="pr_q4">Welche Zahlungsarten?</summary><p data-i18n="pr_a4">Rechnung.</p></details>
    </div>
  </div>
</section>
"""

ABOUT = f"""
<section class="section">
  <div class="wrap">
    <span class="kicker" data-i18n="nav_about">Über uns</span>
    <h1 class="h2" data-i18n="ab_h1">Über uns</h1>
    <div class="prose">
      <p class="lead" data-i18n="ab_lead">meldbar entsteht in Zürich, aus einer einfachen Beobachtung.</p>
      <p class="reveal" data-i18n="ab_p1"></p>
      <p class="reveal" data-i18n="ab_p2"></p>
    </div>
    <div class="values">
      <div class="feature reveal"><div class="ico">{ICONS[1]}</div><h3 data-i18n="ab_v1_t">Aus den Quellen</h3><p data-i18n="ab_v1_p"></p></div>
      <div class="feature reveal d1"><div class="ico">{ICONS[2]}</div><h3 data-i18n="ab_v2_t">Offen</h3><p data-i18n="ab_v2_p"></p></div>
      <div class="feature reveal d2"><div class="ico">{ICONS[6]}</div><h3 data-i18n="ab_v3_t">Ohne Neugier</h3><p data-i18n="ab_v3_p"></p></div>
    </div>
    <div class="prose"><p class="reveal" data-i18n="ab_p3"></p></div>
    <p style="margin-top:24px"><a class="btn primary lg" href="kontakt.html" data-i18n="ab_cta">Schreiben Sie uns</a></p>
  </div>
</section>
"""

CONTACT = """
<section class="section">
  <div class="wrap">
    <span class="kicker" data-i18n="nav_contact">Kontakt</span>
    <h1 class="h2" data-i18n="ct_h1">Kontakt</h1>
    <p class="lead" data-i18n="ct_lead">Fragen zum Produkt, zum Abonnement oder zum Pilotversuch? Schreiben Sie uns.</p>
    <div class="contact-grid">
      <form class="form card" id="contact-form" data-to="kontakt@meldbar.ch">
        <label><span data-i18n="ct_name">Name</span><input name="name" type="text" autocomplete="name" required></label>
        <label><span data-i18n="ct_org">Organisation</span><input name="org" type="text" autocomplete="organization"></label>
        <label><span data-i18n="ct_msg">Nachricht</span><textarea name="message" rows="6" required></textarea></label>
        <button class="btn primary lg" type="submit" data-i18n="ct_send">E-Mail öffnen</button>
        <p class="small muted" data-i18n="ct_note">Der Knopf öffnet Ihr E-Mail-Programm mit dem ausgefüllten Text - diese Seite sendet nichts und speichert nichts.</p>
      </form>
      <div class="info-list">
        <div><h3 data-i18n="ct_email_t">E-Mail</h3><p><a href="mailto:kontakt@meldbar.ch">kontakt@meldbar.ch</a></p></div>
        <div><h3 data-i18n="ct_address_t">Adresse</h3><p>meldbar<br>Salvatorstrasse 8<br>8050 Zürich</p></div>
        <div><h3 data-i18n="ct_hours_t">Erreichbarkeit</h3><p data-i18n="ct_hours">Montag bis Freitag, 9-17 Uhr.</p></div>
        <div class="pilot"><h3 data-i18n="ct_pilot_t">Pilotinstitut werden</h3><p data-i18n="ct_pilot_p"></p></div>
      </div>
    </div>
  </div>
</section>
"""

IMPRINT = """
<section class="section legal">
  <div class="wrap">
    <h1 class="h2" data-i18n="im_h1">Impressum</h1>
    <h2 data-i18n="im_operator">Betreiber dieser Website</h2>
    <p>meldbar<br>Salvatorstrasse 8<br>8050 Zürich<br>Schweiz</p>
    <h2 data-i18n="im_contact">Kontakt</h2>
    <p><a href="mailto:kontakt@meldbar.ch">kontakt@meldbar.ch</a></p>
    <h2 data-i18n="im_liability_t">Haftung</h2>
    <p data-i18n="im_liability"></p>
    <h2 data-i18n="im_links_t">Quellen</h2>
    <p data-i18n="im_links"></p>
  </div>
</section>
"""

PRIVACY = """
<section class="section legal">
  <div class="wrap">
    <h1 class="h2" data-i18n="dp_h1">Datenschutzerklärung</h1>
    <p class="lead" data-i18n="dp_p1"></p>
    <h2 data-i18n="dp_h_hosting">Hosting</h2><p data-i18n="dp_hosting"></p>
    <h2 data-i18n="dp_h_cookies">Cookies und Analytics</h2><p data-i18n="dp_cookies"></p>
    <h2 data-i18n="dp_h_registry">Registerdatei</h2><p data-i18n="dp_registry"></p>
    <h2 data-i18n="dp_h_contact">Kontakt</h2><p data-i18n="dp_contact"></p>
    <h2 data-i18n="dp_h_law">Rechtsgrundlage</h2><p data-i18n="dp_law"></p>
  </div>
</section>
"""

PAGES = {
    "index.html": (
        "home",
        "meldbar - CRS-Meldungen an die ESTV, ohne Installation",
        HOME,
        "CRS-Meldungen für das AIA-Portal der ESTV prüfen, erstellen und verschlüsseln - im Browser, ohne Installation, ohne dass Kontodaten den Rechner verlassen.",
    ),
    "preise.html": (
        "pricing",
        "meldbar - Preise",
        PRICING,
        "Preise von meldbar: kostenlose Web-App, Abonnement pro Organisation, Lizenz für Softwarehäuser.",
    ),
    "ueber-uns.html": (
        "about",
        "meldbar - Über uns",
        ABOUT,
        "Wer hinter meldbar steht und warum das Werkzeug so gebaut ist.",
    ),
    "kontakt.html": (
        "contact",
        "meldbar - Kontakt",
        CONTACT,
        "Kontakt zu meldbar: Fragen zum Produkt, zum Abonnement, zum Pilotversuch.",
    ),
    "impressum.html": ("imprint", "meldbar - Impressum", IMPRINT, "Impressum von meldbar.ch."),
    "datenschutz.html": (
        "privacy",
        "meldbar - Datenschutz",
        PRIVACY,
        "Datenschutzerklärung von meldbar.ch: keine Server-Verarbeitung, keine Cookies, keine Analytics.",
    ),
}


def main() -> int:
    for file, (name, title, body, desc) in PAGES.items():
        (WEB / file).write_text(page(name, title, body, desc=desc), encoding="utf-8")
        print(f"wrote web/{file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
