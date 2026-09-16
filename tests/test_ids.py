"""Tests for MessageRefId / DocRefId rules and the Anhang 7.2 character set."""

import pytest

from aeoi.estv import ids


def test_message_ref_id_shape():
    value = ids.message_ref_id(2026)
    assert value.startswith("CH2026CH")
    check = ids.check_message_ref_id(value)
    assert check.ok and check.year == 2026
    assert len(value) <= ids.MESSAGE_REF_ID_MAX_LEN


def test_wegleitung_example_message_ref_id():
    check = ids.check_message_ref_id("CH2017CH8b0f7048-e2ff-11e6-bf01-fe55135034f3")
    assert check.ok and check.year == 2017


@pytest.mark.parametrize(
    "value",
    ["ch2026CHabc", "CH26CHabc", "CH2026CH", "DE2026CHabc", "CH2026CH" + "x" * 163],
)
def test_bad_message_ref_ids(value):
    assert not ids.check_message_ref_id(value).ok


def test_doc_ref_id_shape_and_year_consistency():
    value = ids.doc_ref_id(2026)
    assert ids.check_doc_ref_id(value, message_year=2026).ok
    assert not ids.check_doc_ref_id(value, message_year=2025).ok


@pytest.mark.parametrize(
    "value", ["CH2026CH", "CH2026CH" + "a" * 43, "CH2026CHa b", "CH2026CHa#b", "CH2026CHa/b"]
)
def test_bad_doc_ref_ids(value):
    assert not ids.check_doc_ref_id(value).ok


def test_year_must_have_four_digits():
    with pytest.raises(ValueError):
        ids.message_ref_id(26)


def test_character_set_accepts_latin1_letters():
    assert ids.is_clean("Müller & Söhne, Zürich (CH) 'Rue de l'Étang' 12; 100% ok? yes.")


@pytest.mark.parametrize(
    "ch", ["!", '"', "#", "$", "<", ">", "^", "~", "£", "§", "©", "°", "½", "÷"]
)
def test_excluded_characters(ch):
    problems = ids.invalid_characters(f"abc{ch}def")
    assert problems and problems[0].position == 3


def test_non_latin1_rejected():
    problems = ids.invalid_characters("Zürich €")
    assert [p.reason for p in problems] == ["not in ISO 8859-1"]


@pytest.mark.parametrize("seq", ["--", "/*", "&#"])
def test_forbidden_sequences(seq):
    problems = ids.invalid_characters(f"ab{seq}cd")
    assert any(p.text == seq for p in problems)


def test_pilcrow_is_not_excluded():
    # U+00B6 is absent from the Anhang 7.2 table; keep the rule literal until the ESTV says otherwise
    assert ids.is_clean("a¶b")
