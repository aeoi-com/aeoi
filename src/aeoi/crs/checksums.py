"""IBAN and ISIN checks as the ESTV applies them (Wegleitung 5.3.7, rules 60000 and 60001).

60000 - AcctNumberType OECD601: "2 Buchstaben & korrekte Prüfsumme & max. 30 Buchstaben oder
        Ziffern" -> ISO 13616 mod-97 check on the whole string (country + 2 check digits + BBAN).
60001 - AcctNumberType OECD603: "2 Buchstaben & 9 Buchstaben oder Ziffern & korrekte Prüfsumme"
        -> ISO 6166: 12 characters, Luhn over the digit expansion (A=10 ... Z=35).
"""

from __future__ import annotations

import re

IBAN_RE = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$")
ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")


def _digits(s: str) -> str:
    return "".join(str(ord(ch) - 55) if ch.isalpha() else ch for ch in s)


def normalise(value: str) -> str:
    return re.sub(r"[\s-]", "", value or "").upper()


def is_valid_iban(value: str) -> bool:
    v = normalise(value)
    if not IBAN_RE.match(v) or len(v) > 34:
        return False
    return int(_digits(v[4:] + v[:4])) % 97 == 1


def is_valid_isin(value: str) -> bool:
    v = normalise(value)
    if not ISIN_RE.match(v):
        return False
    digits = _digits(v)
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 0:  # rightmost digit (the check digit) is position 0 and is not doubled
            total += d
        else:
            d *= 2
            total += d - 9 if d > 9 else d
    return total % 10 == 0
