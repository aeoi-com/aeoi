# aeoi - Kurzfassung für Verbände und ihre Mitglieder

Stand: September 2026. Für Treuhänder, Trust Companies, Family Offices und Vermögensverwalter,
die für ihre Vehikel AIA-Meldungen (CRS) an die ESTV einreichen. Eine Seite; die technischen
Belege stehen in `docs/de/WAS-AENDERT-SICH-MIT-3.0.md` und `docs/de/ANLEITUNG.md`.

## Worum es geht

Die Meldungen für das Jahr 2026 (Frist 30. Juni 2027, Art. 15 Abs. 1 AIAG) sind die ersten, die
im neuen OECD-Schema CRS 3.0 erstellt werden müssen. Das Portal der ESTV nimmt «bis zum
14.12.2026 nur die Version 2.0» und «ab dem 16.1.2027 nur noch die Version 3.0» an (Technische
Wegleitung AIA, September 2026, Ziffer 5.3.1). Das Schema 3.0 verlangt pro Konto neue
Pflichtangaben (Selbstauskunft, Sorgfaltsverfahren, Kontotyp, Typ der beherrschenden Personen);
eine Datei im alten Aufbau wird ab Januar abgewiesen. Wer die Meldungen bisher im Online-Formular
oder mit einem eigenen Skript erstellt hat, muss den Ablauf anpassen.

## Was aeoi ist

`aeoi` ist ein offenes Werkzeug (Apache-2.0, Quellcode einsehbar), das aus einer Excel-Tabelle
die CRS-XML-Datei erstellt und sie **vor** dem Hochladen so prüft, wie es das Portal tut:

- OECD-Schema 2.0 und 3.0, Zeichensatz, Partnerstaaten des Meldejahrs, IBAN/ISIN-Prüfsummen;
- 59 der 65 Regeln der Technischen Wegleitung, mit dem Fehlercode und dem Wortlaut der ESTV. Die
  übrigen sechs (Transport, Entschlüsselung, Virenscan, Registrierung des Instituts) kann nur
  das Portal prüfen;
- Verschlüsselung und Paketierung nach Ziffer 3.3.1, Testmeldungen mit den richtigen Kennzeichen;
- ein lokales Register der gesendeten Meldungen, damit Korrekturen und Stornierungen mit den
  richtigen Verweisen erstellt werden (Ziffer 6), auch über den Wechsel von 2.0 auf 3.0 hinweg;
- Auswertung der Rückmeldung des Portals: jeder Code wird erklärt.

Wer nichts installieren will, macht den ganzen Ablauf auf einer Webseite direkt im Browser, auf
Deutsch, Französisch oder Italienisch: Vorlage herunterladen, ausgefüllte Vorlage prüfen, Meldung
erstellen und verschlüsseln, Ergebnis des Portals erfassen, im nächsten Jahr korrigieren. Die
Datei verlässt den Browser dabei nicht; nach dem ersten Besuch funktioniert die Seite auch offline.
Das Hochladen ins AIA-Portal bleibt beim Institut.

## Was aeoi nicht ist

Kein Hochladen: das Institut lädt das Paket selbst im AIA-Portal hoch, wie bisher. Keine
Beratung zur Meldepflicht oder zur Klassifizierung von Konten. Keine Garantie vor dem
Pilotversuch: das Werkzeug ist gegen die veröffentlichten Schemata und die Wegleitung gebaut und
durch 187 automatische Tests abgesichert, aber erst eine Testmeldung über das Portal zeigt, ob
die ESTV die Dateien genauso liest.

## Datenschutz

Alles läuft auf dem Rechner des Instituts; Kontodaten verlassen ihn nicht. Die Webseite hat
keinen Server, keine Analytik und kein Protokoll; eine Sicherheitsrichtlinie im Browser
verhindert, dass nach der Dateiauswahl irgendeine Adresse kontaktiert wird. Das Werkzeug
verlangt keine Registrierung und sendet nichts nach Hause.

## Kosten

Das Werkzeug ist und bleibt kostenlos. Geplant ist ein Support-Abonnement **pro Organisation**,
nicht pro Benutzer, mit unbegrenzter Zahl meldender Institute: 900 CHF/Jahr bis 10 Vehikel,
1'500 bis 50, 2'400 darüber; Softwarehäuser 2'500 CHF/Jahr. Pilotinstitute zahlen während des
Pilotversuchs nichts.

## Was wir jetzt suchen: ein bis drei Pilotinstitute

Ein registriertes meldendes Finanzinstitut mit Zugang zum Testkanal des AIA-Portals, das

1. im November 2026 eine Testmeldung im Schema 2.0 hochlädt (prüft den Transportweg:
   Verschlüsselung, Paket, Kennungen),
2. in der Woche vom 16. Januar 2027 eine Testmeldung im Schema 3.0 hochlädt,
3. uns danach nur die Codes und Kennungen aus der Validierungsbestätigung des Portals mitteilt -
   nie die Datei, nie Kontodaten.

Aufwand: rund eine Stunde pro Testmeldung. Testmeldungen werden vom Portal validiert, nicht
weitergeleitet und wöchentlich gelöscht (Ziffer 5.3.5). Die offenen Fragen an die ESTV-Praxis,
die der Pilot beantwortet, stehen in `docs/OPEN-QUESTIONS.md`.

Kontakt: <Name, E-Mail> - Quellcode und Anleitung: https://github.com/aeoi-com/aeoi - Prüfung im Browser: https://aeoi-com.github.io/aeoi/
