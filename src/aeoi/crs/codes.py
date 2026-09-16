"""Code lists of the CRS XML Schema (OECD 3.0, with the values that also exist in 2.0).

Values and meanings are copied from the enumeration documentation of ``CrsXML_v3.0.xsd``,
``oecdcrstypes_v5.0.xsd`` and ``CommonTypesFatcaCrs_v2.0.xsd`` (see docs/SOURCES.md). The
transitional "not reported" values (CRS800, CRS900, CRS1000, CRS1100, CRS1200) are kept apart:
they exist only in 3.0 and only for records first reported under 2.0.
"""

from __future__ import annotations

ACCT_HOLDER_TYPE = {
    "CRS101": "Passive Non-Financial Entity with one or more controlling person that is a Reportable Person",
    "CRS102": "CRS Reportable Person",
    "CRS103": "Passive NFE that is a CRS Reportable Person",
}  # fmt: skip

EQUITY_INTEREST_TYPE = {  # 3.0 only, AccountHolder, 0..n
    "CRS401": "EIH of legal arrangements - trust - settlor",
    "CRS402": "EIH of legal arrangements - trust - trustee",
    "CRS403": "EIH of legal arrangements - trust - protector",
    "CRS404": "EIH of legal arrangements - trust - beneficiary",
    "CRS405": "EIH of legal arrangements - trust - other",
    "CRS406": "EIH of legal arrangements - other - settlor-equivalent",
    "CRS407": "EIH of legal arrangements - other - trustee-equivalent",
    "CRS408": "EIH of legal arrangements - other - protector-equivalent",
    "CRS409": "EIH of legal arrangements - other - beneficiary-equivalent",
    "CRS410": "EIH of legal arrangements - other - other equivalent",
}

PAYMENT_TYPE = {
    "CRS501": "Dividends",
    "CRS502": "Interest",
    "CRS503": "Gross Proceeds/Redemptions",
    "CRS504": "Other - CRS",
}

MESSAGE_TYPE_INDIC = {
    "CRS701": "The message contains new information",
    "CRS702": "The message contains corrections for previously sent information",
    "CRS703": "The message advises there is no data to report",
}

CTRLG_PERSON_TYPE = {
    "CRS801": "CP of legal person - ownership",
    "CRS802": "CP of legal person - other means",
    "CRS803": "CP of legal person - senior managing official",
    "CRS804": "CP of legal arrangement - trust - settlor",
    "CRS805": "CP of legal arrangement - trust - trustee",
    "CRS806": "CP of legal arrangement - trust - protector",
    "CRS807": "CP of legal arrangement - trust - beneficiary",
    "CRS808": "CP of legal arrangement - trust - other",
    "CRS809": "CP of legal arrangement - other - settlor-equivalent",
    "CRS810": "CP of legal arrangement - other - trustee-equivalent",
    "CRS811": "CP of legal arrangement - other - protector-equivalent",
    "CRS812": "CP of legal arrangement - other - beneficiary-equivalent",
    "CRS813": "CP of legal arrangement - other - other-equivalent",
}

SELF_CERT = {"CRS901": "True - valid self-certification obtained", "CRS902": "False"}  # 3.0 only
SELF_CERT_CP = {"CRS1001": "True - valid self-certification obtained", "CRS1002": "False"}  # 3.0
ACCOUNT_TYPE = {  # 3.0 only
    "CRS1101": "Depository Account",
    "CRS1102": "Custodial Account",
    "CRS1103": "Cash Value Insurance Contract or Annuity Contract",
    "CRS1104": "Debt or Equity Interest in Investment Entity",
}
DD_PROCEDURE = {"CRS1201": "New Account", "CRS1202": "Preexisting Account"}  # 3.0 only

TRANSITIONAL = {  # 3.0 only, for records first reported under 2.0; ESTV acceptance is an open question
    "CRS800": "CtrlgPersonType not reported",
    "CRS900": "SelfCert (account holder) not reported",
    "CRS1000": "SelfCert (controlling person) not reported",
    "CRS1100": "AccountType not reported",
    "CRS1200": "DDProcedure not reported",
}

DOC_TYPE_INDIC = {
    "OECD0": "Resend Data",
    "OECD1": "New Data",
    "OECD2": "Corrected Data",
    "OECD3": "Deletion of Data",
    "OECD10": "Resend Test Data",
    "OECD11": "New Test Data",
    "OECD12": "Corrected Test Data",
    "OECD13": "Deletion of Test Data",
}

NAME_TYPE = {  # OECD201 is forbidden by the ESTV (rule 60004)
    "OECD202": "indiv (individual)",
    "OECD203": "alias",
    "OECD204": "nick (nickname)",
    "OECD205": "aka (also known as)",
    "OECD206": "dba (doing business as)",
    "OECD207": "legal (legal name)",
    "OECD208": "atbirth (name at birth)",
}

LEGAL_ADDRESS_TYPE = {
    "OECD301": "residentialOrBusiness",
    "OECD302": "residential",
    "OECD303": "business",
    "OECD304": "registeredOffice",
    "OECD305": "unspecified",
}

ACCT_NUMBER_TYPE = {
    "OECD601": "IBAN",
    "OECD602": "OBAN",
    "OECD603": "ISIN",
    "OECD604": "OSIN",
    "OECD605": "Other",
    "OECD606": "Specified Electronic Money Product",
}

NO_ACCOUNT_NUMBER = "NANUM"  # Wegleitung 5.3.7
NO_FIRST_NAME = "NFN"  # Wegleitung 5.3.8
