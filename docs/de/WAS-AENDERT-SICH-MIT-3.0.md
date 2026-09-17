# Was ändert sich mit dem CRS-XML-Schema 3.0 (AIA-Meldungen an die ESTV)

Stand: September 2026. Quellen: Technische Wegleitung AIA der ESTV (September 2026), OECD
CRS XML Schema v3.0 mit User Guide v4.0 (Oktober 2024), OECD CRS Status Message User Guide v3.0
(Juni 2025). Zitate im Original; die Fundstellen sind Ziffern der Technischen Wegleitung.

## Die Daten

- Der revidierte CRS gilt in der Schweiz seit dem 1. Januar 2026; die ESTV hat die Technische
  Wegleitung im September 2026 an das neue Schema angepasst.
- Das Portal der ESTV nimmt Dateien nach Version an: **«Bis zum 14.12.2026 wird nur die Version
  2.0 unterstützt. Ab dem 16.1.2027 wird nur noch die Version 3.0 unterstützt.»** (Ziffer 5.3.1).
  Was zwischen dem 15. Dezember 2026 und dem 15. Januar 2027 gilt, sagt die Wegleitung nicht.
- Die Meldungen für das Jahr 2026 sind bis zum **30. Juni 2027** einzureichen (Art. 15 Abs. 1
  AIAG; Ziffer 2.2.1). Die ESTV erinnert am 1. Juni (Ziffer 2.2.2). Diese Meldungen sind also
  die ersten, die im Schema 3.0 erstellt werden müssen.

## Was im Schema 3.0 neu und zwingend ist

Geprüft am OECD-Schema `CrsXML_v3.0.xsd`; die ESTV nennt dieselben Elemente in den Ziffern
5.3.7 bis 5.3.10 (Regeln 60017-60023).

| Element | Wo | 2.0 | 3.0 | Werte |
|---|---|---|---|---|
| `SelfCert` | Kontoinhaber | gibt es nicht | **zwingend** | CRS901 gültige Selbstauskunft, CRS902 keine |
| `SelfCert` | beherrschende Person | gibt es nicht | **zwingend** | CRS1001 / CRS1002 |
| `CtrlgPersonType` | beherrschende Person | optional, einer | **zwingend, mehrere möglich** | CRS801-CRS813 |
| `DDProcedure` | Konto | gibt es nicht | **zwingend** | CRS1201 Neukonto, CRS1202 bestehendes Konto |
| `AccountType` | Konto | gibt es nicht | **zwingend** | CRS1101 Einlagenkonto, CRS1102 Verwahrkonto, CRS1103 rückkaufsfähiger Versicherungs-/Rentenvertrag, CRS1104 Eigen-/Fremdkapitalbeteiligung |
| `JointAccount` | Konto | gibt es nicht | optional | Anzahl Mitinhaber (1-200) |
| `EquityInterestType` | Kontoinhaber | gibt es nicht | optional, mehrere | CRS401-CRS410 (Rolle bei Trusts und ähnlichen Rechtsgebilden) |

Zusätzliche Prüfregeln der ESTV zu diesen Elementen (Ziffer 5.3.7): ein E-Geld-Produkt
(OECD606) und eine IBAN (OECD601) sind Einlagenkonten (CRS1101); wer `EquityInterestType`
angibt, meldet ein Konto vom Typ CRS1104; ein Versicherungs-/Rentenvertrag (CRS1103) hat die
Kontonummernart OECD605; Einlagenkonten melden nur Zinsen (CRS502), CRS1103 und CRS1104 nur
Bruttoerlöse oder sonstige Zahlungen (CRS503/CRS504).

Für Konten, die vor dem revidierten CRS eröffnet wurden, muss `EquityInterestType` nur
geliefert werden, «wenn diese in seinen elektronisch durchsuchbaren Daten verfügbar sind»
(Ziffer 5.3.8, für die ersten zwei Meldezeiträume).

## Übergangswerte

Das OECD-Schema 3.0 enthält für die neuen Pflichtelemente Werte «not reported», gedacht für
Datensätze, die noch unter 2.0 gemeldet wurden: CRS900 (SelfCert Kontoinhaber), CRS1000
(SelfCert beherrschende Person), CRS800 (CtrlgPersonType), CRS1100 (AccountType), CRS1200
(DDProcedure). Die Technische Wegleitung erwähnt sie nicht. Ob die ESTV sie akzeptiert, ist
offen; relevant wird das, sobald ein 2026 gemeldeter Datensatz im Jahr 2027 korrigiert oder
storniert werden muss.

## Was gleich bleibt

- Der Aufbau der Meldung (MessageSpec, ReportingFI, ReportingGroup mit AccountReports), die
  MessageRefId `CH<Jahr>CH<UUID>`, die DocRefId `CH<Jahr>CH<1-42 Zeichen>`, die Verschlüsselung
  (Ziffer 3.3), die Testmeldungen (DocTypeIndic OECD10/OECD11, Dateiname «Test…»), das
  Korrekturverfahren (Ziffer 6).
- Der Zeichensatz: nur ISO 8859-1 ohne die Zeichen des Anhangs 7.2 (unter anderem `! " # $ < >
  ^ ~ § ° ½`), nie die Folgen `--`, `/*`, `&#`. Ein einziges falsches Zeichen führt zur Ablehnung
  der ganzen Datei (Fehler 50005).

## Das Online-Formular des Portals

Wer die Daten von Hand im Portal erfasst, sollte Folgendes wissen (Ziffer 4.1.2):

- «Aufgrund des Umfangs des CRS-XML-Schemas und der Fehleranfälligkeit der manuellen Dateneingabe
  wird davon abgeraten, eine grössere Anzahl von Datensätzen auf diesem Weg zu erfassen.»
- «Über das Online-Formular erfasste Meldungen können nicht korrigiert, sondern nur storniert und
  neu erfasst werden.»
- Der Inhalt einer per Formular erfassten Meldung «kann über das Portal nicht mehr abgerufen
  werden» - die Aufbewahrung liegt beim Institut.
- Das Formular bildet «die Möglichkeiten des CRS-XML nicht vollständig ab».

Der XML-Upload (oder die M2M-Schnittstelle) ist der Weg für alle, die mehr als einzelne Konten
melden oder Korrekturen brauchen.

## Ein offener Punkt zum Header

Die Wegleitung zeigt in Ziffer 5.3.1 den Header einer 3.0-Datei mit dem Namensraum
`urn:oecd:ties:crs:v2` und `version="3.0"`. Das OECD-Schema 3.0 verwendet aber den Namensraum
`urn:oecd:ties:crs:v3`. Eine Datei, die dem Beispiel der Wegleitung wörtlich folgt, entspricht
dem OECD-Schema nicht. Wir schreiben 3.0-Dateien im OECD-Namensraum und klären den Punkt mit der
ersten Testmeldung nach dem 16. Januar 2027.

## Was das Werkzeug `aeoi` daraus macht

- Aus einer Excel-Vorlage (eine Zeile pro Konto) wird die XML-Datei erstellt, wahlweise nach
  Schema 2.0 (bis 14.12.2026) oder 3.0 (ab 16.01.2027). Die neuen Pflichtfelder sind in der
  Vorlage Spalten mit Auswahllisten; fehlen sie beim Erstellen einer 3.0-Datei, nennt die Prüfung
  jede betroffene Zeile.
- Vor dem Verschlüsseln werden die Datei gegen das OECD-Schema und gegen 59 der 65 Prüfregeln
  der Technischen Wegleitung geprüft (Partnerstaaten des Berichtsjahrs, IBAN/ISIN-Prüfsummen,
  Zeichensatz, Querbezüge der neuen Elemente).
- Ein lokales Register merkt sich alle gesendeten Kennungen. Korrekturen und Stornierungen
  werden daraus aufgebaut - auch für Datensätze, die noch unter 2.0 gemeldet wurden.
