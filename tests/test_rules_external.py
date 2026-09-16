"""Rules that need data outside the message: partner states by year, IBAN/ISIN checksums."""

import datetime as dt

import pytest

from aeoi.crs import checksums, model
from aeoi.crs.example import sample_message
from aeoi.estv import partners

TODAY = dt.date(2027, 3, 1)


def _rules(msg, version="3.0"):
    return {(p.where, p.rule) for p in model.check_message(msg, version, today=TODAY).problems}


def test_partner_list_is_pinned_and_plausible():
    src = partners.source()
    assert src["source_url"].startswith("https://www.sif.admin.ch/")
    assert src["source_stand"] and len(src["page_sha256"]) == 64
    assert src["table_sha256"] == partners.table_sha256()  # the pin is the canonical table
    assert src["count"] >= 100
    assert {"DE", "FR", "IT", "GB", "AU", "JP", "CN"} <= partners.partner_codes(2026)
    assert "US" not in partners.partner_codes(2026)  # FATCA, not CRS
    assert "CH" not in partners.partner_codes(2026)


def test_partner_states_depend_on_the_reporting_year():
    assert partners.is_partner("DE", 2017)
    assert not partners.is_partner("UG", 2025) and partners.is_partner("UG", 2026)
    assert not partners.is_partner("KE", 2023) and partners.is_partner("KE", 2024)
    assert "RU" in partners.partner_codes(2026)  # suspended transmission, data still collected
    assert "suspended" in " ".join(partners.notes("RU"))


def test_98200_individual_outside_partner_states():
    msg = sample_message()
    msg.accounts[0].holder_person.residence_countries = ["US"]
    assert ("Accounts[key=A1].holder.residence_countries", "98200") in _rules(msg)
    # undocumented accounts are the exception (CH only)
    msg.accounts[0].undocumented = True
    msg.accounts[0].holder_person.residence_countries = ["CH"]
    assert not any(r == "98200" for _, r in _rules(msg))


def test_98201_organisation_saved_by_controlling_person():
    msg = sample_message()
    org = msg.accounts[1]
    org.holder_organisation.residence_countries = ["US"]
    assert not any(r == "98201" for _, r in _rules(msg))  # CP resides in FR
    org.controlling_persons[0].person.residence_countries = ["US"]
    rules = _rules(msg)
    assert ("Accounts[key=A2].holder.residence_countries", "98201") in rules
    assert ("Accounts[key=A2].controlling_persons[0].residence_countries", "98202") in rules


def test_partner_state_of_a_later_year_is_not_active_earlier():
    msg = sample_message(year=2025)
    msg.accounts[0].holder_person.residence_countries = ["UG"]  # in force 01.01.2026
    assert ("Accounts[key=A1].holder.residence_countries", "98200") in _rules(msg)
    msg = sample_message(year=2026)
    msg.accounts[0].holder_person.residence_countries = ["UG"]
    assert not any(r == "98200" for _, r in _rules(msg))


@pytest.mark.parametrize(
    "value,ok",
    [
        ("CH9300762011623852957", True),
        ("CH93 0076 2011 6238 5295 7", True),
        ("DE89370400440532013000", True),
        ("GB82WEST12345698765432", True),
        ("CH9300762011623852958", False),
        ("CH93", False),
        ("1234567890", False),
    ],
)
def test_iban(value, ok):
    assert checksums.is_valid_iban(value) is ok


@pytest.mark.parametrize(
    "value,ok",
    [("US0378331005", True), ("CH0038863350", True), ("DE0005190003", True),
     ("US0378331006", False), ("US037833100", False), ("CH00388633500", False)],
)  # fmt: skip
def test_isin(value, ok):
    assert checksums.is_valid_isin(value) is ok


def test_60000_and_60001_in_check_message():
    msg = sample_message()
    msg.accounts[0].account_number = "CH9300762011623852958"  # bad checksum, OECD601
    assert ("Accounts[key=A1].account_number", "60000") in _rules(msg)
    msg = sample_message()
    msg.accounts[1].account_number = "US0378331006"
    msg.accounts[1].account_number_type = "OECD603"
    msg.accounts[1].account_type = "CRS1102"
    msg.accounts[1].equity_interest_types = []
    assert ("Accounts[key=A2].account_number", "60001") in _rules(msg)


def test_eu_agreement_territories_are_partner_states():
    """SIF footnote 6: the EU agreement also applies to Aland, French Guiana, Guadeloupe,
    Martinique, Mayotte, Reunion and Saint-Martin, which have their own ISO codes."""
    for code in ("AX", "GF", "GP", "MQ", "YT", "RE", "MF"):
        assert partners.is_partner(code, 2017), code
        assert any("footnote 6" in n for n in partners.notes(code))
    msg = sample_message()
    msg.accounts[0].holder_person.residence_countries = ["RE"]
    assert not any(r == "98200" for _, r in _rules(msg))


def test_messages_show_the_way_out():
    msg = sample_message()
    msg.accounts[0].holder_person.residence_countries = ["US"]
    texts = [
        p.message
        for p in model.check_message(msg, "3.0", today=TODAY).problems
        if p.rule == "98200"
    ]
    assert texts and "FATCA" in texts[0]
    msg = sample_message()
    msg.accounts[1].controlling_persons[0].person.residence_countries = ["CH"]
    texts = [
        p.message
        for p in model.check_message(msg, "3.0", today=TODAY).problems
        if p.rule == "98202"
    ]
    assert texts and "CRS102 or CRS103" in texts[0]


def test_iban_is_written_normalised():
    from aeoi.crs import build

    msg = sample_message()
    msg.accounts[0].account_number = "ch93 0076-2011 6238 5295 7"
    problems = model.check_message(msg, "3.0", today=TODAY).problems
    assert any(p.rule == "info" and "will be written as" in p.message for p in problems)
    assert not [p for p in problems if p.rule != "info"]
    xml = build.build(msg, "3.0").xml
    assert "CH9300762011623852957" in xml and "ch93 0076" not in xml
