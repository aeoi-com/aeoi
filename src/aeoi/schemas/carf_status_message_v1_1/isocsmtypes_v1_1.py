from __future__ import annotations

from enum import Enum

__NAMESPACE__ = "urn:oecd:ties:isocsmtypes:v1"


class CountryCodeType(Enum):
    """
    ISO-3166 Alpha 2 country codes.

    Attributes:
        AF: AFGHANISTAN
        AX: ALAND ISLANDS
        AL: ALBANIA
        DZ: ALGERIA
        AS: AMERICAN SAMOA
        AD: ANDORRA
        AO: ANGOLA
        AI: ANGUILLA
        AQ: ANTARCTICA
        AG: ANTIGUA AND BARBUDA
        AR: ARGENTINA
        AM: ARMENIA
        AW: ARUBA
        AU: AUSTRALIA
        AT: AUSTRIA
        AZ: AZERBAIJAN
        BS: BAHAMAS
        BH: BAHRAIN
        BD: BANGLADESH
        BB: BARBADOS
        BY: BELARUS
        BE: BELGIUM
        BZ: BELIZE
        BJ: BENIN
        BM: BERMUDA
        BT: BHUTAN
        BO: BOLIVIA, PLURINATIONAL STATE OF
        BQ: BONAIRE, SINT EUSTATIUS AND SABA
        BA: BOSNIA AND HERZEGOVINA
        BW: BOTSWANA
        BV: BOUVET ISLAND
        BR: BRAZIL
        IO: BRITISH INDIAN OCEAN TERRITORY
        BN: BRUNEI DARUSSALAM
        BG: BULGARIA
        BF: BURKINA FASO
        BI: BURUNDI
        KH: CAMBODIA
        CM: CAMEROON
        CA: CANADA
        CV: CABO VERDE
        KY: CAYMAN ISLANDS
        CF: CENTRAL AFRICAN REPUBLIC
        TD: CHAD
        CL: CHILE
        CN: CHINA
        CX: CHRISTMAS ISLAND
        CC: COCOS (KEELING) ISLANDS
        CO: COLOMBIA
        KM: COMOROS
        CG: CONGO
        CD: CONGO, THE DEMOCRATIC REPUBLIC OF THE
        CK: COOK ISLANDS
        CR: COSTA RICA
        CI: COTE D'IVOIRE
        HR: CROATIA
        CU: CUBA
        CW: CURACAO
        CY: CYPRUS
        CZ: CZECHIA
        DK: DENMARK
        DJ: DJIBOUTI
        DM: DOMINICA
        DO: DOMINICAN REPUBLIC
        EC: ECUADOR
        EG: EGYPT
        SV: EL SALVADOR
        GQ: EQUATORIAL GUINEA
        ER: ERITREA
        EE: ESTONIA
        ET: ETHIOPIA
        FK: FALKLAND ISLANDS (MALVINAS)
        FO: FAROE ISLANDS
        FJ: FIJI
        FI: FINLAND
        FR: FRANCE
        GF: FRENCH GUIANA
        PF: FRENCH POLYNESIA
        TF: FRENCH SOUTHERN TERRITORIES
        GA: GABON
        GM: GAMBIA
        GE: GEORGIA
        DE: GERMANY
        GH: GHANA
        GI: GIBRALTAR
        GR: GREECE
        GL: GREENLAND
        GD: GRENADA
        GP: GUADELOUPE
        GU: GUAM
        GT: GUATEMALA
        GG: GUERNSEY
        GN: GUINEA
        GW: GUINEA-BISSAU
        GY: GUYANA
        HT: HAITI
        HM: HEARD ISLAND AND MCDONALD ISLANDS
        VA: HOLY SEE (VATICAN CITY STATE)
        HN: HONDURAS
        HK: HONG KONG
        HU: HUNGARY
        IS: ICELAND
        IN: INDIA
        ID: INDONESIA
        IR: IRAN, ISLAMIC REPUBLIC OF
        IQ: IRAQ
        IE: IRELAND
        IM: ISLE OF MAN
        IL: ISRAEL
        IT: ITALY
        JM: JAMAICA
        JP: JAPAN
        JE: JERSEY
        JO: JORDAN
        KZ: KAZAKHSTAN
        KE: KENYA
        KI: KIRIBATI
        KP: KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF
        KR: KOREA, REPUBLIC OF
        KW: KUWAIT
        KG: KYRGYZSTAN
        LA: LAO PEOPLE'S DEMOCRATIC REPUBLIC
        LV: LATVIA
        LB: LEBANON
        LS: LESOTHO
        LR: LIBERIA
        LY: LIBYA
        LI: LIECHTENSTEIN
        LT: LITHUANIA
        LU: LUXEMBOURG
        MO: MACAO
        MK: NORTH MACEDONIA
        MG: MADAGASCAR
        MW: MALAWI
        MY: MALAYSIA
        MV: MALDIVES
        ML: MALI
        MT: MALTA
        MH: MARSHALL ISLANDS
        MQ: MARTINIQUE
        MR: MAURITANIA
        MU: MAURITIUS
        YT: MAYOTTE
        MX: MEXICO
        FM: MICRONESIA, FEDERATED STATES OF
        MD: MOLDOVA, REPUBLIC OF
        MC: MONACO
        MN: MONGOLIA
        ME: MONTENEGRO
        MS: MONTSERRAT
        MA: MOROCCO
        MZ: MOZAMBIQUE
        MM: MYANMAR
        NA: NAMIBIA
        NR: NAURU
        NP: NEPAL
        NL: NETHERLANDS
        NC: NEW CALEDONIA
        NZ: NEW ZEALAND
        NI: NICARAGUA
        NE: NIGER
        NG: NIGERIA
        NU: NIUE
        NF: NORFOLK ISLAND
        MP: NORTHERN MARIANA ISLANDS
        NO: NORWAY
        OM: OMAN
        PK: PAKISTAN
        PW: PALAU
        PS: PALESTINE, STATE OF
        PA: PANAMA
        PG: PAPUA NEW GUINEA
        PY: PARAGUAY
        PE: PERU
        PH: PHILIPPINES
        PN: PITCAIRN
        PL: POLAND
        PT: PORTUGAL
        PR: PUERTO RICO
        QA: QATAR
        RE: REUNION
        RO: ROMANIA
        RU: RUSSIAN FEDERATION
        RW: RWANDA
        BL: SAINT BARTHELEMY
        SH: SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA
        KN: SAINT KITTS AND NEVIS
        LC: SAINT LUCIA
        MF: SAINT MARTIN (FRENCH PART)
        PM: SAINT PIERRE AND MIQUELON
        VC: SAINT VINCENT AND THE GRENADINES
        WS: SAMOA
        SM: SAN MARINO
        ST: SAO TOME AND PRINCIPE
        SA: SAUDI ARABIA
        SN: SENEGAL
        RS: SERBIA
        SC: SEYCHELLES
        SL: SIERRA LEONE
        SG: SINGAPORE
        SX: SINT MAARTEN (DUTCH PART)
        SK: SLOVAKIA
        SI: SLOVENIA
        SB: SOLOMON ISLANDS
        SO: SOMALIA
        ZA: SOUTH AFRICA
        GS: SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS
        SS: SOUTH SUDAN
        ES: SPAIN
        LK: SRI LANKA
        SD: SUDAN
        SR: SURINAME
        SJ: SVALBARD AND JAN MAYEN
        SZ: ESWATINI
        SE: SWEDEN
        CH: SWITZERLAND
        SY: SYRIAN ARAB REPUBLIC
        TW: TAIWAN, PROVINCE OF CHINA
        TJ: TAJIKISTAN
        TZ: TANZANIA, UNITED REPUBLIC OF
        TH: THAILAND
        TL: TIMOR-LESTE
        TG: TOGO
        TK: TOKELAU
        TO: TONGA
        TT: TRINIDAD AND TOBAGO
        TN: TUNISIA
        TR: TURKEY
        TM: TURKMENISTAN
        TC: TURKS AND CAICOS ISLANDS
        TV: TUVALU
        UG: UGANDA
        UA: UKRAINE
        AE: UNITED ARAB EMIRATES
        GB: UNITED KINGDOM OF GREAT BRITAIN AND NORTHERN IRELAND
        US: UNITED STATES
        UM: UNITED STATES MINOR OUTLYING ISLANDS
        UY: URUGUAY
        UZ: UZBEKISTAN
        VU: VANUATU
        VE: VENEZUELA, BOLIVARIAN REPUBLIC OF
        VN: VIET NAM
        VG: VIRGIN ISLANDS, BRITISH
        VI: VIRGIN ISLANDS, U.S.
        WF: WALLIS AND FUTUNA
        EH: WESTERN SAHARA
        YE: YEMEN
        ZM: ZAMBIA
        ZW: ZIMBABWE
        XK: KOSOVO
    """

    AF = "AF"
    AX = "AX"
    AL = "AL"
    DZ = "DZ"
    AS = "AS"
    AD = "AD"
    AO = "AO"
    AI = "AI"
    AQ = "AQ"
    AG = "AG"
    AR = "AR"
    AM = "AM"
    AW = "AW"
    AU = "AU"
    AT = "AT"
    AZ = "AZ"
    BS = "BS"
    BH = "BH"
    BD = "BD"
    BB = "BB"
    BY = "BY"
    BE = "BE"
    BZ = "BZ"
    BJ = "BJ"
    BM = "BM"
    BT = "BT"
    BO = "BO"
    BQ = "BQ"
    BA = "BA"
    BW = "BW"
    BV = "BV"
    BR = "BR"
    IO = "IO"
    BN = "BN"
    BG = "BG"
    BF = "BF"
    BI = "BI"
    KH = "KH"
    CM = "CM"
    CA = "CA"
    CV = "CV"
    KY = "KY"
    CF = "CF"
    TD = "TD"
    CL = "CL"
    CN = "CN"
    CX = "CX"
    CC = "CC"
    CO = "CO"
    KM = "KM"
    CG = "CG"
    CD = "CD"
    CK = "CK"
    CR = "CR"
    CI = "CI"
    HR = "HR"
    CU = "CU"
    CW = "CW"
    CY = "CY"
    CZ = "CZ"
    DK = "DK"
    DJ = "DJ"
    DM = "DM"
    DO = "DO"
    EC = "EC"
    EG = "EG"
    SV = "SV"
    GQ = "GQ"
    ER = "ER"
    EE = "EE"
    ET = "ET"
    FK = "FK"
    FO = "FO"
    FJ = "FJ"
    FI = "FI"
    FR = "FR"
    GF = "GF"
    PF = "PF"
    TF = "TF"
    GA = "GA"
    GM = "GM"
    GE = "GE"
    DE = "DE"
    GH = "GH"
    GI = "GI"
    GR = "GR"
    GL = "GL"
    GD = "GD"
    GP = "GP"
    GU = "GU"
    GT = "GT"
    GG = "GG"
    GN = "GN"
    GW = "GW"
    GY = "GY"
    HT = "HT"
    HM = "HM"
    VA = "VA"
    HN = "HN"
    HK = "HK"
    HU = "HU"
    IS = "IS"
    IN = "IN"
    ID = "ID"
    IR = "IR"
    IQ = "IQ"
    IE = "IE"
    IM = "IM"
    IL = "IL"
    IT = "IT"
    JM = "JM"
    JP = "JP"
    JE = "JE"
    JO = "JO"
    KZ = "KZ"
    KE = "KE"
    KI = "KI"
    KP = "KP"
    KR = "KR"
    KW = "KW"
    KG = "KG"
    LA = "LA"
    LV = "LV"
    LB = "LB"
    LS = "LS"
    LR = "LR"
    LY = "LY"
    LI = "LI"
    LT = "LT"
    LU = "LU"
    MO = "MO"
    MK = "MK"
    MG = "MG"
    MW = "MW"
    MY = "MY"
    MV = "MV"
    ML = "ML"
    MT = "MT"
    MH = "MH"
    MQ = "MQ"
    MR = "MR"
    MU = "MU"
    YT = "YT"
    MX = "MX"
    FM = "FM"
    MD = "MD"
    MC = "MC"
    MN = "MN"
    ME = "ME"
    MS = "MS"
    MA = "MA"
    MZ = "MZ"
    MM = "MM"
    NA = "NA"
    NR = "NR"
    NP = "NP"
    NL = "NL"
    NC = "NC"
    NZ = "NZ"
    NI = "NI"
    NE = "NE"
    NG = "NG"
    NU = "NU"
    NF = "NF"
    MP = "MP"
    NO = "NO"
    OM = "OM"
    PK = "PK"
    PW = "PW"
    PS = "PS"
    PA = "PA"
    PG = "PG"
    PY = "PY"
    PE = "PE"
    PH = "PH"
    PN = "PN"
    PL = "PL"
    PT = "PT"
    PR = "PR"
    QA = "QA"
    RE = "RE"
    RO = "RO"
    RU = "RU"
    RW = "RW"
    BL = "BL"
    SH = "SH"
    KN = "KN"
    LC = "LC"
    MF = "MF"
    PM = "PM"
    VC = "VC"
    WS = "WS"
    SM = "SM"
    ST = "ST"
    SA = "SA"
    SN = "SN"
    RS = "RS"
    SC = "SC"
    SL = "SL"
    SG = "SG"
    SX = "SX"
    SK = "SK"
    SI = "SI"
    SB = "SB"
    SO = "SO"
    ZA = "ZA"
    GS = "GS"
    SS = "SS"
    ES = "ES"
    LK = "LK"
    SD = "SD"
    SR = "SR"
    SJ = "SJ"
    SZ = "SZ"
    SE = "SE"
    CH = "CH"
    SY = "SY"
    TW = "TW"
    TJ = "TJ"
    TZ = "TZ"
    TH = "TH"
    TL = "TL"
    TG = "TG"
    TK = "TK"
    TO = "TO"
    TT = "TT"
    TN = "TN"
    TR = "TR"
    TM = "TM"
    TC = "TC"
    TV = "TV"
    UG = "UG"
    UA = "UA"
    AE = "AE"
    GB = "GB"
    US = "US"
    UM = "UM"
    UY = "UY"
    UZ = "UZ"
    VU = "VU"
    VE = "VE"
    VN = "VN"
    VG = "VG"
    VI = "VI"
    WF = "WF"
    EH = "EH"
    YE = "YE"
    ZM = "ZM"
    ZW = "ZW"
    XK = "XK"


class LanguageCodeType(Enum):
    """
    ISO 639 - Part 1 Language codes.

    Attributes:
        AA: Afar
        AB: Abkhazian
        AF: Afrikaans
        AK: Akan
        SQ: Albanian
        AM: Amharic
        AR: Arabic
        AN: Aragonese
        HY: Armenian
        AS: Assamese
        AV: Avaric
        AE: Avestan
        AY: Aymara
        AZ: Azerbaijani
        BA: Bashkir
        BM: Bambara
        EU: Basque
        BE: Belarusian
        BN: Bengali
        BH: Bihari languages
        BI: Bislama
        BS: Bosnian
        BR: Breton
        BG: Bulgarian
        MY: Burmese
        CA: Catalan; Valencian
        CH: Chamorro
        CE: Chechen
        ZH: Chinese
        CU: Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian;
            Old Church Slavonic
        CV: Chuvash
        KW: Cornish
        CO: Corsican
        CR: Cree
        CS: Czech
        DA: Danish
        DV: Divehi; Dhivehi; Maldivian
        NL: Dutch; Flemish
        DZ: Dzongkha
        EN: English
        EO: Esperanto
        ET: Estonian
        EE: Ewe
        FO: Faroese
        FJ: Fijian
        FI: Finnish
        FR: French
        FY: Western Frisian
        FF: Fulah
        KA: Georgian
        DE: German
        GD: Gaelic; Scottish Gaelic
        GA: Irish
        GL: Galician
        GV: Manx
        EL: Greek
        GN: Guarani
        GU: Gujarati
        HT: Haitian; Haitian Creole
        HA: Hausa
        HE: Hebrew
        HZ: Herero
        HI: Hindi
        HO: Hiri Motu
        HR: Croatian
        HU: Hungarian
        IG: Igbo
        IS: Icelandic
        IO: Ido
        II: Sichuan Yi; Nuosu
        IU: Inuktitut
        IE: Interlingue; Occidental
        IA: Interlingua (International Auxiliary Language Association)
        ID: Indonesian
        IK: Inupiaq
        IT: Italian
        JV: Javanese
        JA: Japanese
        KL: Kalaallisut; Greenlandic
        KN: Kannada
        KS: Kashmiri
        KR: Kanuri
        KK: Kazakh
        KM: Central Khmer
        KI: Kikuyu; Gikuyu
        RW: Kinyarwanda
        KY: Kirghiz; Kyrgyz
        KV: Komi
        KG: Kongo
        KO: Korean
        KJ: Kuanyama; Kwanyama
        KU: Kurdish
        LO: Lao
        LA: Latin
        LV: Latvian
        LI: Limburgan; Limburger; Limburgish
        LN: Lingala
        LT: Lithuanian
        LB: Luxembourgish; Letzeburgesch
        LU: Luba-Katanga
        LG: Ganda
        MK: Macedonian
        MH: Marshallese
        ML: Malayalam
        MI: Maori
        MR: Marathi
        MS: Malay
        MG: Malagasy
        MT: Maltese
        MN: Mongolian
        NA: Nauru
        NV: Navajo; Navaho
        NR: Ndebele, South; South Ndebele
        ND: Ndebele, North; North Ndebele
        NG: Ndonga
        NE: Nepali
        NN: Norwegian Nynorsk; Nynorsk, Norwegian
        NB: Bokmål, Norwegian; Norwegian Bokmål
        NO: Norwegian
        NY: Chichewa; Chewa; Nyanja
        OC: Occitan; Provençal
        OJ: Ojibwa
        OR: Oriya
        OM: Oromo
        OS: Ossetian; Ossetic
        PA: Panjabi; Punjabi
        FA: Persian
        PI: Pali
        PL: Polish
        PT: Portuguese
        PS: Pushto; Pashto
        QU: Quechua
        RM: Romansh
        RO: Romanian; Moldavian; Moldovan
        RN: Rundi
        RU: Russian
        SG: Sango
        SA: Sanskrit
        SI: Sinhala; Sinhalese
        SK: Slovak
        SL: Slovenian
        SE: Northern Sami
        SM: Samoan
        SN: Shona
        SD: Sindhi
        SO: Somali
        ST: Sotho, Southern
        ES: Spanish; Castilian
        SC: Sardinian
        SR: Serbian
        SS: Swati
        SU: Sundanese
        SW: Swahili
        SV: Swedish
        TY: Tahitian
        TA: Tamil
        TT: Tatar
        TE: Telugu
        TG: Tajik
        TL: Tagalog
        TH: Thai
        BO: Tibetan
        TI: Tigrinya
        TO: Tonga (Tonga Islands)
        TN: Tswana
        TS: Tsonga
        TK: Turkmen
        TR: Turkish
        TW: Twi
        UG: Uighur; Uyghur
        UK: Ukrainian
        UR: Urdu
        UZ: Uzbek
        VE: Venda
        VI: Vietnamese
        VO: Volapük
        CY: Welsh
        WA: Walloon
        WO: Wolof
        XH: Xhosa
        YI: Yiddish
        YO: Yoruba
        ZA: Zhuang; Chuang
        ZU: Zulu
    """

    AA = "AA"
    AB = "AB"
    AF = "AF"
    AK = "AK"
    SQ = "SQ"
    AM = "AM"
    AR = "AR"
    AN = "AN"
    HY = "HY"
    AS = "AS"
    AV = "AV"
    AE = "AE"
    AY = "AY"
    AZ = "AZ"
    BA = "BA"
    BM = "BM"
    EU = "EU"
    BE = "BE"
    BN = "BN"
    BH = "BH"
    BI = "BI"
    BS = "BS"
    BR = "BR"
    BG = "BG"
    MY = "MY"
    CA = "CA"
    CH = "CH"
    CE = "CE"
    ZH = "ZH"
    CU = "CU"
    CV = "CV"
    KW = "KW"
    CO = "CO"
    CR = "CR"
    CS = "CS"
    DA = "DA"
    DV = "DV"
    NL = "NL"
    DZ = "DZ"
    EN = "EN"
    EO = "EO"
    ET = "ET"
    EE = "EE"
    FO = "FO"
    FJ = "FJ"
    FI = "FI"
    FR = "FR"
    FY = "FY"
    FF = "FF"
    KA = "KA"
    DE = "DE"
    GD = "GD"
    GA = "GA"
    GL = "GL"
    GV = "GV"
    EL = "EL"
    GN = "GN"
    GU = "GU"
    HT = "HT"
    HA = "HA"
    HE = "HE"
    HZ = "HZ"
    HI = "HI"
    HO = "HO"
    HR = "HR"
    HU = "HU"
    IG = "IG"
    IS = "IS"
    IO = "IO"
    II = "II"
    IU = "IU"
    IE = "IE"
    IA = "IA"
    ID = "ID"
    IK = "IK"
    IT = "IT"
    JV = "JV"
    JA = "JA"
    KL = "KL"
    KN = "KN"
    KS = "KS"
    KR = "KR"
    KK = "KK"
    KM = "KM"
    KI = "KI"
    RW = "RW"
    KY = "KY"
    KV = "KV"
    KG = "KG"
    KO = "KO"
    KJ = "KJ"
    KU = "KU"
    LO = "LO"
    LA = "LA"
    LV = "LV"
    LI = "LI"
    LN = "LN"
    LT = "LT"
    LB = "LB"
    LU = "LU"
    LG = "LG"
    MK = "MK"
    MH = "MH"
    ML = "ML"
    MI = "MI"
    MR = "MR"
    MS = "MS"
    MG = "MG"
    MT = "MT"
    MN = "MN"
    NA = "NA"
    NV = "NV"
    NR = "NR"
    ND = "ND"
    NG = "NG"
    NE = "NE"
    NN = "NN"
    NB = "NB"
    NO = "NO"
    NY = "NY"
    OC = "OC"
    OJ = "OJ"
    OR = "OR"
    OM = "OM"
    OS = "OS"
    PA = "PA"
    FA = "FA"
    PI = "PI"
    PL = "PL"
    PT = "PT"
    PS = "PS"
    QU = "QU"
    RM = "RM"
    RO = "RO"
    RN = "RN"
    RU = "RU"
    SG = "SG"
    SA = "SA"
    SI = "SI"
    SK = "SK"
    SL = "SL"
    SE = "SE"
    SM = "SM"
    SN = "SN"
    SD = "SD"
    SO = "SO"
    ST = "ST"
    ES = "ES"
    SC = "SC"
    SR = "SR"
    SS = "SS"
    SU = "SU"
    SW = "SW"
    SV = "SV"
    TY = "TY"
    TA = "TA"
    TT = "TT"
    TE = "TE"
    TG = "TG"
    TL = "TL"
    TH = "TH"
    BO = "BO"
    TI = "TI"
    TO = "TO"
    TN = "TN"
    TS = "TS"
    TK = "TK"
    TR = "TR"
    TW = "TW"
    UG = "UG"
    UK = "UK"
    UR = "UR"
    UZ = "UZ"
    VE = "VE"
    VI = "VI"
    VO = "VO"
    CY = "CY"
    WA = "WA"
    WO = "WO"
    XH = "XH"
    YI = "YI"
    YO = "YO"
    ZA = "ZA"
    ZU = "ZU"
