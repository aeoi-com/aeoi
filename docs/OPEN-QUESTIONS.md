# Open questions for the pilot reporting FI (and, through it, the ESTV AIA team)

Each item names the source that raised it. Answers go back into the rule engine with a test.

1. **Namespace of the 3.0 header.** The OECD `CrsXML_v3.0.xsd` declares
   `targetNamespace="urn:oecd:ties:crs:v3"`. The ESTV Technische Wegleitung (09.2026), Ziffer 5.3.1,
   shows the 3.0 header as `<crs:CRS_OECD version="3.0" ... xmlns:crs="urn:oecd:ties:crs:v2" ...>` and all
   annex examples (7.1) are still 2.0 documents. A file that follows the Wegleitung literally fails
   XSD validation against the OECD 3.0 schema; a file that follows the OECD schema deviates from the
   Wegleitung example. Working assumption: the Wegleitung example is a leftover and the portal
   validates against the OECD 3.0 schema (`crs:v3`). To be settled by the first 3.0 test upload in
   the week of 16.01.2027. The validator supports both and reports the mismatch explicitly.

2. **Gap between 14.12.2026 and 16.01.2027.** Wegleitung 5.3.1: "Bis zum 14.12.2026 wird nur die
   Version 2.0 unterstützt. Ab dem 16.1.2027 wird nur noch die Version 3.0 unterstützt." What the
   portal accepts in between (nothing? both?) is not written. Ask the pilot to check the portal
   notice in December.

3. **Element name `EquityInterestType` vs `EntityInterestType`.** The XSD 3.0 and xsdata models say
   `EquityInterestType` (on AccountHolder); the Wegleitung change log (5.3.8/5.3.9) says
   "EntityInterestType". Presumably a typo in the Wegleitung; the XSD wins for generation, the
   rule text quotes both.

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

## Policy for the pilot exchange

The pilot sends **validation results** (DocRefId, error codes, texts), never the CRS file: the
file contains account-holder data and the MessageRefId must not contain customer data either
(Wegleitung 5.3.2). No account data ever reaches the toolkit maintainers.
