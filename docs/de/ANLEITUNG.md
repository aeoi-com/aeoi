# aeoi - Anleitung für meldende Finanzinstitute und Treuhänder

`aeoi` erstellt aus einer Excel-Tabelle die CRS-XML-Datei für das AIA-Portal der ESTV, prüft sie
vorher wie das Portal, verschlüsselt sie zum Hochladen und merkt sich, was gesendet wurde, damit
Korrekturen und Stornierungen möglich sind. Alles läuft auf Ihrem Rechner; keine Kontodaten
verlassen ihn.

Voraussetzungen: Python 3.11 oder neuer, Zugang zum AIA-Portal der ESTV als registriertes
meldendes Finanzinstitut (für Testmeldungen und den öffentlichen Schlüssel der ESTV).

## 1. Installation

Bis das Paket auf PyPI veröffentlicht ist, installieren Sie aus dem Repository:

```bash
pip install "aeoi @ git+https://<repository-url>"
aeoi --version
```

(Später: `pip install aeoi`.)

## 2. Vorlage ausfüllen

```bash
aeoi crs template --out meldung-2026.xlsx
```

Die Datei hat vier Blätter:

- **ReportingFI**: Ihr Institut - ESTV-ID (`SendingCompanyIN`), UID (leer lassen, wenn das
  Institut keine hat), Name, Adresse, Meldejahr. Bei einem Trustee-Documented Trust: den Namen
  des Trusts eintragen und `trustee_documented_trust = true` setzen; das Präfix «TDT=» wird beim
  Erstellen angefügt.
- **Accounts**: eine Zeile pro meldepflichtiges Konto. `holder_type` ist `individual`
  (natürliche Person; Spalten Vorname … Nationalitäten) oder `organisation` (Rechtsträger;
  Spalten `org_name`, `acct_holder_type`, `org_ins`). Gelbe Spalten sind Pflicht, orange nur für
  den jeweiligen Inhabertyp. Die Spalten `self_cert`, `dd_procedure`, `account_type` (und
  optional `joint_account_number`, `equity_interest_types`) sind für das Schema 3.0 Pflicht.
- **ControllingPersons**: beherrschende Personen eines Rechtsträgers mit `acct_holder_type`
  CRS101; `key` verweist auf die Kontozeile.
- **Payments**: Zahlungen des Jahres; `key` verweist auf die Kontozeile.

Konventionen: mehrere Werte in einer Zelle mit `;` trennen (`CH;DE`); TIN als `Nummer@Land`;
Ja/Nein-Spalten mit `true`/`false` (auch `ja`/`nein`); Daten als `JJJJ-MM-TT` oder Excel-Datum.
Das Blatt **Codes** erklärt jeden Code, das Blatt **ReadMe** die Regeln (Gemeinschaftskonten:
eine Zeile pro meldepflichtigen Mitinhaber mit dem vollen Saldo und `joint_account_number`).

Erlaubte Zeichen: nur ISO 8859-1 ohne `! " # $ < > ^ ~` und die Sonderzeichen des Anhangs 7.2
(zum Beispiel `§ ° ½ ©`), nie `--`, `/*`, `&#`. Die Prüfung nennt jede betroffene Zelle.

## 3. Prüfen

```bash
aeoi crs check --input meldung-2026.xlsx --version 3.0
```

Bis zum 14.12.2026 nimmt das Portal nur Schema 2.0 an (`--version 2.0`), ab dem 16.01.2027 nur
3.0. Jede Meldung endet mit der Zeile, der Spalte und der Nummer der ESTV-Regel, zum Beispiel:

```
error  | Accounts[key=A7].holder.residence_countries: none of ['US'] was a Swiss AEOI partner
         state in 2026 (SIF list, Stand 25.08.2026) (US is not an AEOI partner state: US persons
         fall under FATCA, not the CRS); the account is not reportable under the CRS for this year [98200]
```

`info`-Zeilen sind Hinweise (zum Beispiel: eine IBAN wird ohne Leerzeichen geschrieben).

## 4. XML erstellen und verschlüsseln

Den öffentlichen Schlüssel der ESTV finden Sie im AIA-Portal an zwei Stellen (Technische
Wegleitung, Ziffer 3.3): das AIA-Zertifikat auf der Seite für den XML-Upload (Ziffer 3.3.1) oder
die Datei `ESTV-PublicKey.pem` im Archiv `estv-encryptor-*.zip` des ESTV-Encryptors (Ziffer
3.3.2). `aeoi` nimmt beides mit `--key` entgegen.

```bash
aeoi crs build --input meldung-2026.xlsx --version 3.0 --out meldung-2026.xml \
    --registry institut.sqlite --key ESTV-PublicKey.pem --package meldung-2026.zip
```

Das Werkzeug prüft die Tabelle, erstellt die XML-Datei, prüft sie gegen das OECD-Schema, trägt
die Kennungen (MessageRefId, DocRefIds) im Register `institut.sqlite` ein und erzeugt das
verschlüsselte Paket, das Sie im Portal hochladen.

**Testmeldung** (jederzeit möglich, wird validiert und nicht weitergeleitet, Ziffer 5.3.5):
`--test` anfügen und das Paket `Test-….zip` nennen. Das Werkzeug setzt dann die
Test-Kennzeichen (OECD11 usw.) und verweigert einen Dateinamen ohne «Test». Beachten Sie:
«Testmeldungen werden wöchentlich in der Nacht von Samstag auf Sonntag gelöscht» (Ziffer 5.3.5)
- das Ergebnis also vorher aus der Meldungsübersicht sichern.

Eine vorhandene XML-Datei - auch aus einem anderen Programm - prüfen Sie mit
`aeoi crs validate datei.xml`.

## 5. Ergebnis erfassen

Nach dem Hochladen zeigt das Portal in der AIA-Meldungsübersicht eine Validierungsbestätigung
oder einen Fehlerbericht. Speichern Sie den Text (oder die Statusmeldung als XML) in eine Datei
und erfassen Sie ihn im Register:

```bash
aeoi estv status ergebnis.txt --registry institut.sqlite --message CH2026CH…
```

Jeder Fehlercode wird mit Ziffer und Seite der Technischen Wegleitung erklärt. Erst nach
einer erfassten Bestätigung kann ein Datensatz korrigiert werden.

## 6. Korrigieren und stornieren

Korrigieren Sie die Zeilen in derselben Excel-Datei und rufen Sie auf:

```bash
aeoi crs correct --input meldung-2026.xlsx --version 3.0 --out korrektur-1.xml \
    --registry institut.sqlite --cancel A7 --key ESTV-PublicKey.pem --package korrektur-1.zip
```

- Geänderte Zeilen werden als Korrektur (OECD2) gesendet, `--cancel KEY` storniert ein Konto
  (OECD3), unveränderte Zeilen werden weggelassen, neue Zeilen gehören in eine neue Meldung
  (`aeoi crs build`).
- Die Kette der Korrekturen (Ziffer 6.3.3) führt das Register: jede Korrektur verweist auf den
  zuletzt gültigen Datensatz; ein storniertes Konto kann nicht korrigiert, nur neu gemeldet
  werden; das ReportingFI wird mit der bekannten DocRefId erneut gesendet.
- Datensätze, die noch unter Schema 2.0 gemeldet wurden, können unter 3.0 korrigiert und
  storniert werden.

`aeoi crs registry --registry institut.sqlite` zeigt alle Meldungen mit Status; `--discard`
kennzeichnet eine erstellte, aber nie hochgeladene Meldung.

## 7. Datenschutz

Das Register enthält die Kontodaten, die für Stornierungen nötig sind. Bewahren Sie es zusammen
mit der Excel-Datei auf, sichern Sie es, und senden Sie es niemandem. Bei Rückfragen an den
Support des Werkzeugs genügen der Fehlercode, die DocRefId und die MessageRefId - nie die Datei
(Ziffer 5.3.2: die MessageRefId darf keine Kundendaten enthalten).

## Fristen 2027

- 14.12.2026: letzter Tag für Dateien nach Schema 2.0.
- 16.01.2027: erster Tag für Dateien nach Schema 3.0.
- 30.06.2027: Einreichungsfrist für das Meldejahr 2026 (Erinnerung der ESTV am 1. Juni).
