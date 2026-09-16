from __future__ import annotations

from enum import Enum

__NAMESPACE__ = "urn:oecd:ties:isocarftypes:v1"


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


class CurrCodeType(Enum):
    """
    The appropriate currency code from the ISO 4217 three-byte alpha
    version for the currency in which a monetary amount is expressed.

    Attributes:
        AED: UAE Dirham: UNITED ARAB EMIRATES
        AFN: Afghani: AFGHANISTAN
        ALL: Lek: ALBANIA
        AMD: Armenian Dram: ARMENIA
        ANG: Netherlands Antillean Guilder: CURACAO; SINT MAARTEN (DUTCH
            PART)
        AOA: Kwanza: ANGOLA
        ARS: Argentine Peso: ARGENTINA
        AUD: Australian Dollar: AUSTRALIA; CHRISTMAS ISLAND; COCOS
            (KEELING) ISLANDS; HEARD ISLAND AND McDONALD ISLANDS;
            KIRIBATI; NAURU; NORFOLK ISLAND; TUVALU
        AWG: Aruban Florin: ARUBA
        AZN: Azerbaijan Manat: AZERBAIJAN
        BAM: Convertible Mark: BOSNIA AND HERZEGOVINA
        BBD: Barbados Dollar: BARBADOS
        BDT: Taka: BANGLADESH
        BGN: Bulgarian Lev: BULGARIA
        BHD: Bahraini Dinar: BAHRAIN
        BIF: Burundi Franc: BURUNDI
        BMD: Bermudian Dollar: BERMUDA
        BND: Brunei Dollar: BRUNEI DARUSSALAM
        BOB: Boliviano: BOLIVIA, PLURINATIONAL STATE OF
        BOV: Mvdol: BOLIVIA, PLURINATIONAL STATE OF
        BRL: Brazilian Real: BRAZIL
        BSD: Bahamian Dollar: BAHAMAS
        BTN: Ngultrum: BHUTAN
        BWP: Pula: BOTSWANA
        BYN: Belarusian Ruble: BELARUS
        BYR: Historic use: Belarussian Ruble: BELARUS
        BZD: Belize Dollar: BELIZE
        CAD: Canadian Dollar: CANADA
        CDF: Congolese Franc: CONGO, THE DEMOCRATIC REPUBLIC OF
        CHE: WIR Euro: SWITZERLAND
        CHF: Swiss Franc: LIECHTENSTEIN; SWITZERLAND
        CHW: WIR Franc: SWITZERLAND
        CLF: Unidad de Fomento: CHILE
        CLP: Chilean Peso: CHILE
        CNY: Yuan Renminbi: CHINA
        COP: Colombian Peso: COLOMBIA
        COU: Unidad de Valor Real: COLOMBIA
        CRC: Costa Rican Colon: COSTA RICA
        CUC: Peso Convertible: CUBA
        CUP: Cuban Peso: CUBA
        CVE: Cabo Verde Escudo: CABO VERDE
        CZK: Czech Koruna: CZECHIA
        DJF: Djibouti Franc: DJIBOUTI
        DKK: Danish Krone: DENMARK; FAROE ISLANDS; GREENLAND
        DOP: Dominican Peso: DOMINICAN REPUBLIC
        DZD: Algerian Dinar: ALGERIA
        EGP: Egyptian Pound: EGYPT
        ERN: Nakfa: ERITREA
        ETB: Ethiopian Birr: ETHIOPIA
        EUR: Euro: ALAND ISLANDS; ANDORRA; AUSTRIA; BELGIUM; CYPRUS;
            ESTONIA; EUROPEAN UNION; FINLAND; FRANCE; FRENCH GUIANA;
            FRENCH SOUTHERN TERRITORIES; GERMANY; GREECE; GUADELOUPE;
            HOLY SEE (VATICAN CITY STATE); IRELAND; ITALY; LATVIA;
            LITHUANIA; LUXEMBOURG; MALTA; MARTINIQUE; MAYOTTE; MONACO;
            MONTENEGRO; NETHERLANDS; PORTUGAL; REUNION; SAINT
            BARTHELEMY; SAINT MARTIN (FRENCH PART); SAINT PIERRE AND
            MIQUELON; SAN MARINO; SLOVAKIA; SLOVENIA; SPAIN; Vatican
            City State (HOLY SEE)
        FJD: Fiji Dollar: FIJI
        FKP: Falkland Islands Pound: FALKLAND ISLANDS (MALVINAS)
        GBP: Pound Sterling: GUERNSEY; ISLE OF MAN; JERSEY; UNITED
            KINGDOM OF GREAT BRITAIN AND NORTHERN IRELAND
        GEL: Lari: GEORGIA
        GHS: Ghana Cedi: GHANA
        GIP: Gibraltar Pound: GIBRALTAR
        GMD: Dalasi: GAMBIA
        GNF: Guinean Franc: GUINEA
        GTQ: Quetzal: GUATEMALA
        GYD: Guyana Dollar: GUYANA
        HKD: Hong Kong Dollar: HONG KONG
        HNL: Lempira: HONDURAS
        HRK: Kuna: CROATIA
        HTG: Gourde: HAITI
        HUF: Forint: HUNGARY
        IDR: Rupiah: INDONESIA
        ILS: New Israeli Sheqel: ISRAEL
        INR: Indian Rupee: BHUTAN; INDIA
        IQD: Iraqi Dinar: IRAQ
        IRR: Iranian Rial: IRAN, ISLAMIC REPUBLIC OF
        ISK: Iceland Krona: ICELAND
        JMD: Jamaican Dollar: JAMAICA
        JOD: Jordanian Dinar: JORDAN
        JPY: Yen: JAPAN
        KES: Kenyan Shilling: KENYA
        KGS: Som: KYRGYZSTAN
        KHR: Riel: CAMBODIA
        KMF: Comorian Franc : COMOROS
        KPW: North Korean Won: KOREA, DEMOCRATIC PEOPLE’S REPUBLIC OF
        KRW: Won: KOREA, REPUBLIC OF
        KWD: Kuwaiti Dinar: KUWAIT
        KYD: Cayman Islands Dollar: CAYMAN ISLANDS
        KZT: Tenge: KAZAKHSTAN
        LAK: Lao Kip: LAO PEOPLE’S DEMOCRATIC REPUBLIC
        LBP: Lebanese Pound: LEBANON
        LKR: Sri Lanka Rupee: SRI LANKA
        LRD: Liberian Dollar: LIBERIA
        LSL: Loti: LESOTHO
        LTL: Historic use: Lithuanian Litas: LITHUANIA
        LVL: Historic use: Latvian Lats: LATVIA
        LYD: Libyan Dinar: LIBYA
        MAD: Moroccan Dirham: MOROCCO; WESTERN SAHARA
        MDL: Moldovan Leu: MOLDOVA, REPUBLIC OF
        MGA: Malagasy Ariary: MADAGASCAR
        MKD: Denar: MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF
        MMK: Kyat: MYANMAR
        MNT: Tugrik: MONGOLIA
        MOP: Pataca: MACAO
        MRO: Historic use: Ouguiya: MAURITANIA
        MRU: Ouguiya: MAURITANIA
        MUR: Mauritius Rupee: MAURITIUS
        MVR: Rufiyaa: MALDIVES
        MWK: Malawi Kwacha: MALAWI
        MXN: Mexican Peso: MEXICO
        MXV: Mexican Unidad de Inversion (UDI): MEXICO
        MYR: Malaysian Ringgit: MALAYSIA
        MZN: Mozambique Metical: MOZAMBIQUE
        NAD: Namibia Dollar: NAMIBIA
        NGN: Naira: NIGERIA
        NIO: Cordoba Oro: NICARAGUA
        NOK: Norwegian Krone: BOUVET ISLAND; NORWAY; SVALBARD AND JAN
            MAYEN
        NPR: Nepalese Rupee: NEPAL
        NZD: New Zealand Dollar: COOK ISLANDS; NEW ZEALAND; NIUE;
            PITCAIRN; TOKELAU
        OMR: Rial Omani: OMAN
        PAB: Balboa: PANAMA
        PEN: Sol: PERU
        PGK: Kina: PAPUA NEW GUINEA
        PHP: Philippine Peso: PHILIPPINES
        PKR: Pakistan Rupee: PAKISTAN
        PLN: Zloty: POLAND
        PYG: Guarani: PARAGUAY
        QAR: Qatari Rial: QATAR
        RON: Romanian Leu: ROMANIA
        RSD: Serbian Dinar: SERBIA
        RUB: Russian Ruble: RUSSIAN FEDERATION
        RWF: Rwanda Franc: RWANDA
        SAR: Saudi Riyal: SAUDI ARABIA
        SBD: Solomon Islands Dollar: SOLOMON ISLANDS
        SCR: Seychelles Rupee: SEYCHELLES
        SDG: Sudanese Pound: SUDAN
        SEK: Swedish Krona: SWEDEN
        SGD: Singapore Dollar: SINGAPORE
        SHP: Saint Helena Pound: SAINT HELENA, ASCENSION AND TRISTAN DA
            CUNHA
        SLL: Leone: SIERRA LEONE
        SOS: Somali Shilling: SOMALIA
        SRD: Surinam Dollar: SURINAME
        SSP: South Sudanese Pound: SOUTH SUDAN
        STD: Historic use: Dobra: SAO TOME AND PRINCIPE
        STN: Dobra: SAO TOME AND PRINCIPE
        SVC: El Salvador Colon: EL SALVADOR
        SYP: Syrian Pound: SYRIAN ARAB REPUBLIC
        SZL: Lilangeni: ESWATINI
        THB: Baht: THAILAND
        TJS: Somoni: TAJIKISTAN
        TMT: Turkmenistan New Manat: TURKMENISTAN
        TND: Tunisian Dinar: TUNISIA
        TOP: Pa’anga: TONGA
        TRY: Turkish Lira: TURKEY
        TTD: Trinidad and Tobago Dollar: TRINIDAD AND TOBAGO
        TWD: New Taiwan Dollar: TAIWAN, PROVINCE OF CHINA
        TZS: Tanzanian Shilling: TANZANIA, UNITED REPUBLIC OF
        UAH: Hryvnia: UKRAINE
        UGX: Uganda Shilling: UGANDA
        USD: US Dollar: AMERICAN SAMOA; BONAIRE; SINT EUSTATIUS AND
            SABA; BRITISH INDIAN OCEAN TERRITORY; ECUADOR; EL SALVADOR;
            GUAM; HAITI; MARSHALL ISLANDS; MICRONESIA, FEDERATED STATES
            OF; NORTHERN MARIANA ISLANDS; PALAU; PANAMA; PUERTO RICO;
            TIMOR-LESTE; TURKS AND CAICOS ISLANDS; UNITED STATES; UNITED
            STATES MINOR OUTLYING ISLANDS; VIRGIN ISLANDS (BRITISH);
            VIRGIN ISLANDS (US)
        USN: US Dollar (Next day): UNITED STATES
        USS: Historic use: US Dollar (Same day): UNITED STATES
        UYI: Uruguay Peso en Unidades Indexadas (UI): URUGUAY
        UYU: Peso Uruguayo: URUGUAY
        UYW: Unidad Previsional: URUGUAY
        UZS: Uzbekistan Sum: UZBEKISTAN
        VEF: Historic use: Bolivar: VENEZUELA, BOLIVARIAN REPUBLIC OF
        VES: Bolívar Soberano: VENEZUELA, BOLIVARIAN REPUBLIC OF
        VND: Dong: VIET NAM
        VUV: Vatu: VANUATU
        WST: Tala: SAMOA
        XAF: CFA Franc BEAC: CAMEROON; CENTRAL AFRICAN REPUBLIC; CHAD;
            CONGO; EQUATORIAL GUINEA; GABON
        XAG: Silver: ZZ11_Silver
        XAU: Gold: ZZ08_Gold
        XBA: Bond Markets Unit European Composite Unit (EURCO):
            ZZ01_Bond Markets Unit European_EURCO
        XBB: Bond Markets Unit European Monetary Unit (E.M.U.-6):
            ZZ02_Bond Markets Unit European_EMU-6
        XBC: Bond Markets Unit European Unit of Account 9 (E.U.A.-9):
            ZZ03_Bond Markets Unit European_EUA-9
        XBD: Bond Markets Unit European Unit of Account 17 (E.U.A.-17):
            ZZ04_Bond Markets Unit European_EUA-17
        XCD: East Caribbean Dollar: ANGUILLA; ANTIGUA AND BARBUDA;
            DOMINICA; GRENADA; MONTSERRAT; SAINT KITTS AND NEVIS; SAINT
            LUCIA; SAINT VINCENT AND THE GRENADINES
        XDR: SDR (Special Drawing Right): INTERNATIONAL MONETARY FUND
            (IMF)
        XFU: Historic use: UIC-Franc: ZZ05_UIC-Franc
        XOF: CFA Franc BCEAO: BENIN; BURKINA FASO; COTE D'IVOIRE;
            GUINEA-BISSAU; MALI; NIGER; SENEGAL; TOGO
        XPD: Palladium: ZZ09_Palladium
        XPF: CFP Franc: FRENCH POLYNESIA; NEW CALEDONIA; WALLIS AND
            FUTUNA
        XPT: Platinum: ZZ10_Platinum
        XSU: Sucre: SISTEMA UNITARIO DE COMPENSACION REGIONAL DE PAGOS
            "SUCRE"
        XUA: ADB Unit of Account: MEMBER COUNTRIES OF THE AFRICAN
            DEVELOPMENT BANK GROUP
        XXX: The codes assigned for transactions where no currency is
            involved: ZZ07_No_Currency
        YER: Yemeni Rial: YEMEN
        ZAR: Rand: LESOTHO; NAMIBIA; SOUTH AFRICA
        ZMW: Zambian Kwacha: ZAMBIA
        ZWL: Zimbabwe Dollar: ZIMBABWE
    """

    AED = "AED"
    AFN = "AFN"
    ALL = "ALL"
    AMD = "AMD"
    ANG = "ANG"
    AOA = "AOA"
    ARS = "ARS"
    AUD = "AUD"
    AWG = "AWG"
    AZN = "AZN"
    BAM = "BAM"
    BBD = "BBD"
    BDT = "BDT"
    BGN = "BGN"
    BHD = "BHD"
    BIF = "BIF"
    BMD = "BMD"
    BND = "BND"
    BOB = "BOB"
    BOV = "BOV"
    BRL = "BRL"
    BSD = "BSD"
    BTN = "BTN"
    BWP = "BWP"
    BYN = "BYN"
    BYR = "BYR"
    BZD = "BZD"
    CAD = "CAD"
    CDF = "CDF"
    CHE = "CHE"
    CHF = "CHF"
    CHW = "CHW"
    CLF = "CLF"
    CLP = "CLP"
    CNY = "CNY"
    COP = "COP"
    COU = "COU"
    CRC = "CRC"
    CUC = "CUC"
    CUP = "CUP"
    CVE = "CVE"
    CZK = "CZK"
    DJF = "DJF"
    DKK = "DKK"
    DOP = "DOP"
    DZD = "DZD"
    EGP = "EGP"
    ERN = "ERN"
    ETB = "ETB"
    EUR = "EUR"
    FJD = "FJD"
    FKP = "FKP"
    GBP = "GBP"
    GEL = "GEL"
    GHS = "GHS"
    GIP = "GIP"
    GMD = "GMD"
    GNF = "GNF"
    GTQ = "GTQ"
    GYD = "GYD"
    HKD = "HKD"
    HNL = "HNL"
    HRK = "HRK"
    HTG = "HTG"
    HUF = "HUF"
    IDR = "IDR"
    ILS = "ILS"
    INR = "INR"
    IQD = "IQD"
    IRR = "IRR"
    ISK = "ISK"
    JMD = "JMD"
    JOD = "JOD"
    JPY = "JPY"
    KES = "KES"
    KGS = "KGS"
    KHR = "KHR"
    KMF = "KMF"
    KPW = "KPW"
    KRW = "KRW"
    KWD = "KWD"
    KYD = "KYD"
    KZT = "KZT"
    LAK = "LAK"
    LBP = "LBP"
    LKR = "LKR"
    LRD = "LRD"
    LSL = "LSL"
    LTL = "LTL"
    LVL = "LVL"
    LYD = "LYD"
    MAD = "MAD"
    MDL = "MDL"
    MGA = "MGA"
    MKD = "MKD"
    MMK = "MMK"
    MNT = "MNT"
    MOP = "MOP"
    MRO = "MRO"
    MRU = "MRU"
    MUR = "MUR"
    MVR = "MVR"
    MWK = "MWK"
    MXN = "MXN"
    MXV = "MXV"
    MYR = "MYR"
    MZN = "MZN"
    NAD = "NAD"
    NGN = "NGN"
    NIO = "NIO"
    NOK = "NOK"
    NPR = "NPR"
    NZD = "NZD"
    OMR = "OMR"
    PAB = "PAB"
    PEN = "PEN"
    PGK = "PGK"
    PHP = "PHP"
    PKR = "PKR"
    PLN = "PLN"
    PYG = "PYG"
    QAR = "QAR"
    RON = "RON"
    RSD = "RSD"
    RUB = "RUB"
    RWF = "RWF"
    SAR = "SAR"
    SBD = "SBD"
    SCR = "SCR"
    SDG = "SDG"
    SEK = "SEK"
    SGD = "SGD"
    SHP = "SHP"
    SLL = "SLL"
    SOS = "SOS"
    SRD = "SRD"
    SSP = "SSP"
    STD = "STD"
    STN = "STN"
    SVC = "SVC"
    SYP = "SYP"
    SZL = "SZL"
    THB = "THB"
    TJS = "TJS"
    TMT = "TMT"
    TND = "TND"
    TOP = "TOP"
    TRY = "TRY"
    TTD = "TTD"
    TWD = "TWD"
    TZS = "TZS"
    UAH = "UAH"
    UGX = "UGX"
    USD = "USD"
    USN = "USN"
    USS = "USS"
    UYI = "UYI"
    UYU = "UYU"
    UYW = "UYW"
    UZS = "UZS"
    VEF = "VEF"
    VES = "VES"
    VND = "VND"
    VUV = "VUV"
    WST = "WST"
    XAF = "XAF"
    XAG = "XAG"
    XAU = "XAU"
    XBA = "XBA"
    XBB = "XBB"
    XBC = "XBC"
    XBD = "XBD"
    XCD = "XCD"
    XDR = "XDR"
    XFU = "XFU"
    XOF = "XOF"
    XPD = "XPD"
    XPF = "XPF"
    XPT = "XPT"
    XSU = "XSU"
    XUA = "XUA"
    XXX = "XXX"
    YER = "YER"
    ZAR = "ZAR"
    ZMW = "ZMW"
    ZWL = "ZWL"
