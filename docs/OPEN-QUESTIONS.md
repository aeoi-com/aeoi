# Open questions for the pilot reporting FI (and, through it, the ESTV AIA team)

Each item names the source that raised it. Answers go back into the rule engine with a test.

1. **Namespace of the 3.0 header.** The OECD `CrsXML_v3.0.xsd` declares
   `targetNamespace="urn:oecd:ties:crs:v3"`. The ESTV Technische Wegleitung (09.2026), Ziffer 5.3.1,
   shows the 3.0 header as `<crs:CRS_OECD version="3.0" ... xmlns:crs="urn:oecd:ties:crs:v2" ...>` and all
   annex examples (7.1) are still 2.0 documents. A file that follows the Wegleitung literally fails
   XSD validation against the OECD 3.0 schema; a file that follows the OECD schema deviates from the
   Wegleitung example. Working assumption: the Wegleitung example is a leftover and the portal
   validates against the OECD 3.0 schema (`crs:v3`). The generator emits `crs:v3` only; the
   validator accepts both and reports the mismatch. To be settled by the first 3.0 test upload in
   the week of 16.01.2027. Supporting the leftover reading: the French edition of the same
   Wegleitung shows `version="3.0"` with `crs:v2` like the German one, while the Italian
   edition (same date) still shows `version="2.0"` in that very example (5.3.1) - the header
   snippet was evidently edited by hand per language, not generated from a validated file.

2. **Gap between 14.12.2026 and 16.01.2027.** Wegleitung 5.3.1: "Bis zum 14.12.2026 wird nur die
   Version 2.0 unterstützt. Ab dem 16.1.2027 wird nur noch die Version 3.0 unterstützt." What the
   portal accepts in between (nothing? both?) is not written. Ask the pilot to check the portal
   notice in December.

3. **Transitional "not reported" values.** The 3.0 schema carries CRS800 (CtrlgPersonType), CRS900
   (SelfCert of the account holder), CRS1000 (SelfCert of a controlling person), CRS1100
   (AccountType) and CRS1200 (DDProcedure), documented as "available as a transitional measure" for
   records first reported under 2.0. The Wegleitung does not mention them. Does the ESTV accept them,
   and for which reporting years? This decides how a 2026 AccountReport is corrected in 2027.

4. **Status message version returned by the portal.** The Wegleitung refers to the CRS Status Message
   User Guide v3.0 (2025) for codes; the portal shows results in the "AIA Meldungsübersicht" and via
   M2M. Ask the pilot for one real validation report (codes and DocRefIds only, no account data) to
   fix the parser format.

5. **Public key and Encryptor.** Both are only downloadable inside the AIA application (Wegleitung
   3.3.1/3.3.2). Until the pilot shares `ESTV-PublicKey.pem`, the packaging module runs with a
   placeholder key; the structural checks are the same.

6. **Test-message quota or side effects.** Wegleitung 5.3.5: test messages can be sent at any time
   and are validated but not forwarded. Confirm with the pilot that test uploads leave no trace that
   matters for their real filing (they appear in the message overview).

7. **Character `¶` (U+00B6).** Absent from the Anhang 7.2 exclusion table while its neighbours are
   excluded. The validator keeps the table literal; flag if the portal rejects it.

## Closed

- Portal status «Fehler» (Benutzeranleitung): «Der Status «Fehler» erscheint, falls ein
  unbekanntes Problem die Verarbeitung verhinderte. In diesem Fall muss die Datei noch einmal
  hochgeladen werden.» Not a rejection: `status.parse_text` sets `portal_error`, the registry
  keeps the message open (`submitted`), the page says so. The portal's verdict words are
  «Akzeptiert» / «Abgelehnt»; the catalogue uses them.

- **`EquityInterestType` vs `EntityInterestType`** — closed. The body of the Wegleitung (5.3.8 and
  rule 60019) says `EquityInterestType`, matching the XSD; `EntityInterestType` appears only in the
  change log. Typo, not a doubt.

## Rule-text defects handled in the rule engine (Wegleitung 09.2026)

- **60018**: the formula says "Wenn AccountNumber = OECD606" but the prose says "Internationale
  Bankkontonummer (OECD601)". Implement the prose (IBAN = OECD601); note the discrepancy in the
  rule's text.
- **60021**: "Tyoe" for "Type" in the rule text. Cosmetic; keep the code, fix the label.

## Policy for the pilot exchange

The pilot sends **validation results** (DocRefId, error codes, texts), never the CRS file: the
file contains account-holder data and the MessageRefId must not contain customer data either
(Wegleitung 5.3.2). No account data ever reaches the toolkit maintainers.
