"""A fictitious but complete message: example workbook (`aeoi crs template --example`) and tests."""

import datetime as dt
from decimal import Decimal

from aeoi.crs.model import (
    Account,
    Address,
    ControllingPerson,
    Message,
    Organisation,
    Payment,
    Person,
    ReportingFI,
    Tin,
)


def sample_message(year: int = 2026) -> Message:
    fi = ReportingFI(
        estv_id="052.0000.0000",
        uid="CHE-123.456.789",
        name="Beispiel AG",
        address=Address(
            country="CH",
            street="Bahnhofstrasse",
            building_identifier="1",
            post_code="8001",
            city="Zürich",
            legal_address_type="OECD304",
        ),
        contact="AIA Team, +41 44 000 00 00",
    )
    individual = Account(
        key="A1",
        account_number="CH9300762011623852957",
        account_number_type="OECD601",
        holder_person=Person(
            first_name="Anna",
            last_name="Müller",
            birth_date=dt.date(1975, 4, 12),
            birth_city="Berlin",
            birth_country="DE",
            residence_countries=["DE"],
            tins=[Tin(value="12345678901", issued_by="DE")],
            address=Address(
                country="DE",
                street="Unter den Linden",
                building_identifier="5",
                post_code="10117",
                city="Berlin",
            ),
        ),
        balance=Decimal("125000.50"),
        currency="CHF",
        payments=[Payment(payment_type="CRS502", amount=Decimal("1200.00"), currency="CHF")],
        self_cert="CRS901",
        dd_procedure="CRS1202",
        account_type="CRS1101",
    )
    entity = Account(
        key="A2",
        account_number="4711-0815",
        account_number_type="OECD605",
        holder_organisation=Organisation(
            name="Holding Trust Ltd",
            acct_holder_type="CRS101",
            residence_countries=["FR"],
            ins=[Tin(value="FR12345", issued_by="FR")],
            address=Address(
                country="FR",
                street="Rue de Rivoli",
                building_identifier="10",
                post_code="75001",
                city="Paris",
            ),
        ),
        controlling_persons=[
            ControllingPerson(
                person=Person(
                    first_name="Pierre",
                    last_name="Dupont",
                    birth_date=dt.date(1960, 1, 2),
                    residence_countries=["FR"],
                    address=Address(country="FR", city="Lyon", post_code="69001"),
                ),
                ctrlg_person_types=["CRS804", "CRS807"],
                self_cert="CRS1001",
            )
        ],
        balance=Decimal(0),
        currency="EUR",
        closed=True,
        self_cert="CRS902",
        dd_procedure="CRS1201",
        account_type="CRS1104",
        equity_interest_types=["CRS401"],
        payments=[Payment(payment_type="CRS503", amount=Decimal("50.00"), currency="EUR")],
    )
    return Message(reporting_fi=fi, reporting_year=year, accounts=[individual, entity])
