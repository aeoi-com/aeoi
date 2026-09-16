"""Identifiers and character set rules of the ESTV AIA portal.

Sources: Technische Wegleitung AIA (ESTV, 09.2026), Ziffer 5.3.2 (MessageRefId), 5.3.5 and
5.3.11 (DocRefId), 5.1 and Anhang 7.2 (character set).

MessageRefId (error 50008 / 50009)
    ``CH`` + reporting year + ``CH`` + unique id; UUID per RFC 4122 recommended; globally
    unique, never reused; at most 170 characters; regex ``CH[0-9]{4}CH.{1,162}``; must not
    contain customer data because it appears in error messages.

DocRefId (error 80000 / 80001)
    ``CH`` + reporting year + ``CH`` + 1-42 digits, letters, hyphens, underscores or dots;
    the reporting year must equal the one in the MessageRefId; unique across all messages
    ever sent by the FI.

Character set (error 50005)
    Only ISO 8859-1, minus the characters listed in Anhang 7.2, and never the sequences
    ``--``, ``/*``, ``&#``. Control characters (C0 except tab/LF/CR, DEL and C1 0x80-0x9F) are
    part of ISO 8859-1 but have no place in data elements and are rejected here as well.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

MESSAGE_REF_ID_RE = re.compile(r"^CH(?P<year>[0-9]{4})CH(?P<unique>.{1,162})$", re.DOTALL)
MESSAGE_REF_ID_MAX_LEN = 170
DOC_REF_ID_RE = re.compile(r"^CH(?P<year>[0-9]{4})CH(?P<unique>[0-9A-Za-z._-]{1,42})$")

# Anhang 7.2: characters of ISO 8859-1 that are NOT allowed in data elements.
EXCLUDED_CHARS: frozenset[str] = frozenset(
    chr(c)
    for c in (
        0x21, 0x22, 0x23, 0x24, 0x3C, 0x3E, 0x5E, 0x7E,
        0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF,
        0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5, 0xB7, 0xB8, 0xB9, 0xBA, 0xBB, 0xBC, 0xBD, 0xBE, 0xBF,
        0xF7,
    )
)  # fmt: skip
FORBIDDEN_SEQUENCES: tuple[str, ...] = ("--", "/*", "&#")
ALLOWED_CONTROL_CHARS: frozenset[str] = frozenset({chr(0x09), chr(0x0A), chr(0x0D)})


def message_ref_id(reporting_year: int) -> str:
    """New MessageRefId for a message between FI and ESTV: ``CH<year>CH<uuid4>``."""
    _check_year(reporting_year)
    return f"CH{reporting_year}CH{uuid.uuid4()}"


def doc_ref_id(reporting_year: int) -> str:
    """New DocRefId: ``CH<year>CH<uuid4>`` (36 characters, within the 1-42 limit)."""
    _check_year(reporting_year)
    return f"CH{reporting_year}CH{uuid.uuid4()}"


def _check_year(year: int) -> None:
    if not (1000 <= year <= 9999):
        raise ValueError(f"reporting year must have four digits, got {year!r}")


@dataclass(frozen=True)
class IdCheck:
    ok: bool
    year: int | None
    problems: tuple[str, ...]


def check_message_ref_id(value: str) -> IdCheck:
    problems: list[str] = []
    if len(value) > MESSAGE_REF_ID_MAX_LEN:
        problems.append(f"MessageRefId longer than {MESSAGE_REF_ID_MAX_LEN} characters (50008)")
    m = MESSAGE_REF_ID_RE.match(value)
    if not m:
        problems.append("MessageRefId must match CH<year>CH<unique id> (50008)")
        return IdCheck(False, None, tuple(problems))
    bad = invalid_characters(m.group("unique"))
    if bad:
        problems.append("MessageRefId contains characters outside Anhang 7.2 (50008)")
    return IdCheck(not problems, int(m.group("year")), tuple(problems))


def check_doc_ref_id(value: str, *, message_year: int | None = None) -> IdCheck:
    problems: list[str] = []
    m = DOC_REF_ID_RE.match(value)
    if not m:
        problems.append(
            "DocRefId must be CH<year>CH + 1-42 letters, digits, '-', '_' or '.' (80001)"
        )
        return IdCheck(False, None, tuple(problems))
    year = int(m.group("year"))
    if message_year is not None and year != message_year:
        problems.append(
            f"DocRefId year {year} differs from MessageRefId year {message_year} (80001)"
        )
    return IdCheck(not problems, year, tuple(problems))


@dataclass(frozen=True)
class CharProblem:
    position: int
    text: str
    reason: str


def invalid_characters(text: str) -> list[CharProblem]:
    """Characters outside ISO 8859-1, control characters, Anhang 7.2 exclusions and sequences."""
    problems: list[CharProblem] = []
    for i, ch in enumerate(text):
        code = ord(ch)
        if code > 0xFF:
            problems.append(CharProblem(i, ch, "not in ISO 8859-1"))
        elif ch in EXCLUDED_CHARS:
            problems.append(CharProblem(i, ch, f"excluded by Anhang 7.2 (U+{code:04X})"))
        elif (code < 0x20 and ch not in ALLOWED_CONTROL_CHARS) or 0x7F <= code <= 0x9F:
            problems.append(CharProblem(i, ch, f"control character (U+{code:04X})"))
    for seq in FORBIDDEN_SEQUENCES:
        start = 0
        while (pos := text.find(seq, start)) != -1:
            problems.append(CharProblem(pos, seq, "forbidden sequence (Anhang 7.2)"))
            start = pos + 1
    problems.sort(key=lambda p: p.position)
    return problems


def is_clean(text: str) -> bool:
    return not invalid_characters(text)
