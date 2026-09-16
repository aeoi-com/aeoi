# Pinned sources

Manifest: `docs/sources/manifest.json` (regenerated 2026-09-16). File names encode the version the document declares; the hash pins the exact bytes. `python tools/pin_sources.py --fetch` downloads what is missing and checks every hash.

| File | Bytes | SHA-256 | Committed | URL |
|---|---|---|---|---|
| `docs/sources/oecd/crs-xml-schema-v3.0.zip` | 18382 | `71328994cf1e0924c119e78cf2e798bcb0bf6f2939c2f9ab7f3c5d2e0d7915e3` | yes | https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/xml-schema-crs.zip |
| `docs/sources/oecd/crs-xml-schema-user-guide-v4.0-2024-10.pdf` | 3863202 | `7dfc3cac58bff32710f8ab548e10c3d5d4cdc6117a7c0649dc118be359a1862f` | yes | https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/10/amended-common-reporting-standard-xml-schema_27960161/dd7ee57a-en.pdf |
| `docs/sources/oecd/crs-xml-schema-v2.0.zip` | 17549 | `d770d7c426759691c57c89c41d808790f0f3b841e9cb61d514334c55ccb0a524` | yes | https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/crs-schema-v2.0.zip |
| `docs/sources/oecd/crs-xml-schema-user-guide-v3.0-2019-06.pdf` | 5861707 | `7864e5c8bdddd59dbf7f5fd64e80224bb979eeda2324e49f6d154bc2208a79c6` | yes | https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/06/common-reporting-standard-xml-schema-user-guide-for-tax-administrations-version-3-0-june-2019_32dc1e5a/93b6aa4a-en.pdf |
| `docs/sources/oecd/crs-status-message-xml-schema-v2.0.zip` | 8617 | `20dbf04cfba775adb5e32b5e1d6373b5cf97dd6cf1a7b42f8b71a7e13d5826d9` | yes | https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/crs-status-message-v2.0.zip |
| `docs/sources/oecd/crs-status-message-user-guide-v3.0-2025-06.pdf` | 1037972 | `7d6800d3a92c6784544bbeb52a129e47820c987b79c55196fa5a5ca88090038e` | yes | https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/06/common-reporting-standard-status-message-xml-schema_6b5a1079/6c08db84-en.pdf |
| `docs/sources/oecd/crs-status-message-user-guide-v2.0-2019-06.pdf` | 2460269 | `fb865ae709cf69edb0e4a659502d0bdce3e9c8be760ccf6d6673d56222879fe8` | yes | https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/06/common-reporting-standard-status-message-xml-schema-user-guide-for-tax-administrations-version-2-0-june-2019_934c12ea/4aaa6516-en.pdf |
| `docs/sources/oecd/carf-xml-schema-v1.5.zip` | 17208 | `e55d533f88551d41ceec4f4b84258c6ff45116603c37cff3c11581097aa1898b` | yes | https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/xml-schema-carf-v1.5.zip |
| `docs/sources/oecd/carf-xml-schema-user-guide-v2.0-2025-07.pdf` | 2714592 | `72cc636d3c52ad10ec3720e7660d222d85b8a3c93de80de9af0b2604278adec2` | yes | https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/10/crypto-asset-reporting-framework-xml-schema_d15d81d3/578052ec-en.pdf |
| `docs/sources/oecd/carf-status-message-xml-schema-v1.1.zip` | 8687 | `208ef41fdb313bd7c5485eb57a540d77100313835f022dc64f18c4bb40100421` | yes | https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/carf-status-message-xml-schema-v1.1.zip |
| `docs/sources/oecd/generic-status-message-xml-schema-v2.0.zip` | 8953 | `b9f81ad8fa6847b8039f472c53f55afff2d929a83e618fb3271571452f443b23` | yes | https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/generic-status-message-xml-schema-v2.0.zip |
| `docs/sources/estv/estv-technische-wegleitung-aia-2026-09.pdf` | 1664518 | `ab5eb730f6477d84d9262e8c2d50ea7cd1a2d5a64319a3553899783dfd8ad34d` | no | https://www.estv.admin.ch/dam/de/sd-web/nawtcd6uyf89/int-aia-technische-wegleitung-de.pdf |
| `docs/sources/estv/estv-wegleitung-aia-2026-01-15.pdf` | 4063364 | `d13f3c1de784bafcd6abe1a0ed94e9566c9e1bef6538ed1216cca1cfd43cb502` | no | https://www.estv.admin.ch/dam/de/sd-web/hEtJr9vx6Ej-/20260115_Wegleitung_D_Publikation_Clean.pdf |

## What is what

- **CRS XML Schema v3.0** (`CrsXML_v3.0.xsd`, namespace `urn:oecd:ties:crs:v3`) with **User Guide v4.0**
  (October 2024): the business rules for the amended CRS. Only version accepted by the ESTV from
  16.01.2027 (Wegleitung 5.3.1).
- **CRS XML Schema v2.0** (`CrsXML_v2.0.xsd`, namespace `urn:oecd:ties:crs:v2`) with **User Guide v3.0**
  (June 2019): the only version the ESTV accepts until 14.12.2026; used to test the transport pipeline
  before the switch.
- **CRS Status Message XML Schema v2.0** with **User Guide v3.0** (June 2025): the error codes the
  portals return; the ESTV rules refer to it (Wegleitung reference [6]).
- **CARF XML Schema v1.5** with **User Guide v2.0** (July 2025) and **CARF Status Message v1.1**:
  second module.
- **ESTV Technische Wegleitung AIA** (September 2026): Swiss portal rules, 67 error codes,
  packaging/encryption, test messages. **ESTV Wegleitung AIA** (15.01.2026): substantive guidance.
  Not committed; `python tools/pin_sources.py --fetch` downloads them and checks the hash.

## Licences and citations

OECD material is published under CC BY 4.0 (OECD open access policy; pre-July-2024 items may be
copied and distributed for commercial and non-commercial purposes with attribution). Citations in the
form the OECD requests:

- OECD (2024), Amended Common Reporting Standard XML Schema (Version 3.0), https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/xml-schema-crs.zip
- OECD (2024), Amended Common Reporting Standard XML Schema: User Guide for Tax Administrations (Version 4.0), OECD Publishing, Paris, https://doi.org/10.1787/dd7ee57a-en
- OECD (2019), Common Reporting Standard XML Schema (Version 2.0), https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/crs-schema-v2.0.zip
- OECD (2019), Common Reporting Standard XML Schema: User Guide for Tax Administrations, Version 3.0 - June 2019, OECD Publishing, Paris, https://doi.org/10.1787/93b6aa4a-en
- OECD (2019), Common Reporting Standard Status Message XML Schema (Version 2.0), https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/crs-status-message-v2.0.zip
- OECD (2025), Common Reporting Standard Status Message XML Schema: User Guide for Tax Administrations (Version 3.0), OECD Publishing, Paris, https://doi.org/10.1787/6c08db84-en
- OECD (2019), Common Reporting Standard Status Message XML Schema: User Guide for Tax Administrations, Version 2.0 - June 2019, OECD Publishing, Paris, https://doi.org/10.1787/4aaa6516-en
- OECD (2025), Crypto-Asset Reporting Framework XML Schema (Version 1.5), https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/xml-schema-carf-v1.5.zip
- OECD (2025), Crypto-Asset Reporting Framework XML Schema: User Guide for Tax Administrations (Version 2.0), OECD Publishing, Paris, https://doi.org/10.1787/578052ec-en
- OECD (2025), Crypto-Asset Reporting Framework Status Message XML Schema (Version 1.1), https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/carf-status-message-xml-schema-v1.1.zip
- OECD (2020), Generic Status Message XML Schema (Version 2.0), https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/tax-transparency-and-international-co-operation/generic-status-message-xml-schema-v2.0.zip
- ESTV (2026), Technische Wegleitung - Standard fuer den automatischen Informationsaustausch ueber Finanzkonten, Bern, September 2026
- ESTV (2026), Wegleitung - Standard fuer den automatischen Informationsaustausch ueber Finanzkonten, Bern, 15.01.2026

Swiss federal documents: official acts, decisions and reports of authorities are not protected by
copyright (URG Art. 5); a Wegleitung is probably covered but not certainly, hence not redistributed.
