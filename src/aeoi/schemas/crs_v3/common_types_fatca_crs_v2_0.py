from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from aeoi.schemas.crs_v3.isocrstypes_v1_1 import (
    CountryCodeType,
    CurrCodeType,
)
from aeoi.schemas.crs_v3.oecdcrstypes_v5_0 import (
    OecdlegalAddressTypeEnumType,
    OecdnameTypeEnumType,
)

__NAMESPACE__ = "urn:oecd:ties:commontypesfatcacrs:v2"


class AcctNumberTypeEnumType(Enum):
    """
    Account Number Type.

    Attributes:
        OECD601: IBAN
        OECD602: OBAN
        OECD603: ISIN
        OECD604: OSIN
        OECD605: Other
        OECD606: Specified Electronic Money Product
    """

    OECD601 = "OECD601"
    OECD602 = "OECD602"
    OECD603 = "OECD603"
    OECD604 = "OECD604"
    OECD605 = "OECD605"
    OECD606 = "OECD606"


@dataclass(kw_only=True)
class AddressFixType:
    """
    Structure of the address for a party broken down into its logical
    parts, recommended for easy matching.

    The 'City' element is the only required subelement. All of the
    subelements are simple text - data type 'string'.
    """

    class Meta:
        name = "AddressFix_Type"

    street: None | str = field(
        default=None,
        metadata={
            "name": "Street",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
            "min_length": 1,
            "max_length": 200,
        },
    )
    building_identifier: None | str = field(
        default=None,
        metadata={
            "name": "BuildingIdentifier",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
            "min_length": 1,
            "max_length": 200,
        },
    )
    suite_identifier: None | str = field(
        default=None,
        metadata={
            "name": "SuiteIdentifier",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
            "min_length": 1,
            "max_length": 200,
        },
    )
    floor_identifier: None | str = field(
        default=None,
        metadata={
            "name": "FloorIdentifier",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
            "min_length": 1,
            "max_length": 200,
        },
    )
    district_name: None | str = field(
        default=None,
        metadata={
            "name": "DistrictName",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
            "min_length": 1,
            "max_length": 200,
        },
    )
    pob: None | str = field(
        default=None,
        metadata={
            "name": "POB",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
            "min_length": 1,
            "max_length": 200,
        },
    )
    post_code: None | str = field(
        default=None,
        metadata={
            "name": "PostCode",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
            "min_length": 1,
            "max_length": 200,
        },
    )
    city: str = field(
        metadata={
            "name": "City",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
            "min_length": 1,
            "max_length": 200,
        }
    )
    country_subentity: None | str = field(
        default=None,
        metadata={
            "name": "CountrySubentity",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
            "min_length": 1,
            "max_length": 200,
        },
    )


@dataclass(kw_only=True)
class AddressType:
    """
    The user has the option to enter the data about the address of a party
    either as one long field or to spread the data over up to eight
    elements or even to use both formats.

    If the user chooses the option to enter the data required in separate
    elements, the container element for this will be 'AddressFix'. If the
    user chooses the option to enter the data required in a less structured
    way in 'AddressFree' all available address details shall be presented
    as one string of bytes, blank or "/" (slash) or carriage return- line
    feed used as a delimiter between parts of the address. PLEASE NOTE that
    the address country code is outside both of these elements. The use of
    the fixed form is recommended as a rule to allow easy matching.
    However, the use of the free form is recommended if the sending state
    cannot reliably identify and distinguish the different parts of the
    address. The user may want to use both formats e.g. if besides
    separating the logical parts of the address he also wants to indicate a
    suitable breakdown into print-lines by delimiters in the free text
    form. In this case 'AddressFix' has to precede 'AddressFree'.
    """

    class Meta:
        name = "Address_Type"

    country_code: CountryCodeType = field(
        metadata={
            "name": "CountryCode",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
        }
    )
    address_fix: None | AddressFixType = field(
        default=None,
        metadata={
            "name": "AddressFix",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
        },
    )
    address_free: None | str = field(
        default=None,
        metadata={
            "name": "AddressFree",
            "type": "Element",
            "namespace": "urn:oecd:ties:commontypesfatcacrs:v2",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    legal_address_type: None | OecdlegalAddressTypeEnumType = field(
        default=None,
        metadata={
            "name": "legalAddressType",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class MonAmntType:
    """
    This data type is to be used whenever monetary amounts are to be
    communicated.

    Such amounts shall be given including two fractional digits of the main
    currency unit. The code for the currency in which the value is
    expressed has to be taken from the ISO codelist 4217 and added in
    attribute currCode.
    """

    class Meta:
        name = "MonAmnt_Type"

    value: Decimal = field(
        metadata={
            "fraction_digits": 2,
        }
    )
    curr_code: CurrCodeType = field(
        metadata={
            "name": "currCode",
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class NameOrganisationType:
    """
    Name of organisation.
    """

    class Meta:
        name = "NameOrganisation_Type"

    value: str = field(
        default="",
        metadata={
            "min_length": 1,
            "max_length": 200,
        },
    )
    name_type: None | OecdnameTypeEnumType = field(
        default=None,
        metadata={
            "name": "nameType",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class TinType:
    """
    This is the identification number/identification code for the party in
    question.

    As the identifier may be not strictly numeric, it is just defined as a
    string of characters. Attribute 'issuedBy' is required to designate the
    issuer of the identifier.

    Attributes:
        value:
        issued_by: Country code of issuing country, indicating country
            of Residence (to taxes and other)
    """

    class Meta:
        name = "TIN_Type"

    value: str = field(
        default="",
        metadata={
            "min_length": 1,
            "max_length": 200,
        },
    )
    issued_by: None | CountryCodeType = field(
        default=None,
        metadata={
            "name": "issuedBy",
            "type": "Attribute",
        },
    )
