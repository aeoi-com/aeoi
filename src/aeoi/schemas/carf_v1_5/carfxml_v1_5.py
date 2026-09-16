from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from xsdata.models.datatype import XmlDate, XmlDateTime

from aeoi.schemas.carf_v1_5.isocarftypes_v1_1 import (
    CountryCodeType,
    CurrCodeType,
)
from aeoi.schemas.carf_v1_5.oecdcarftypes_v5_0 import (
    DocSpecType,
    OecdlegalAddressTypeEnumType,
    OecdnameTypeEnumType,
)

__NAMESPACE__ = "urn:oecd:ties:carf:v1"


@dataclass(kw_only=True)
class AddressFixType:
    class Meta:
        name = "AddressFix_Type"

    street: None | str = field(
        default=None,
        metadata={
            "name": "Street",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    building_identifier: None | str = field(
        default=None,
        metadata={
            "name": "BuildingIdentifier",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    suite_identifier: None | str = field(
        default=None,
        metadata={
            "name": "SuiteIdentifier",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    floor_identifier: None | str = field(
        default=None,
        metadata={
            "name": "FloorIdentifier",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    district_name: None | str = field(
        default=None,
        metadata={
            "name": "DistrictName",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    pob: None | str = field(
        default=None,
        metadata={
            "name": "POB",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    post_code: None | str = field(
        default=None,
        metadata={
            "name": "PostCode",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    city: str = field(
        metadata={
            "name": "City",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        }
    )
    country_subentity: None | str = field(
        default=None,
        metadata={
            "name": "CountrySubentity",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )


class AltValuationEnumType(Enum):
    """
    Attributes:
        CARF1001: Book value
        CARF1002: Third-party value
        CARF1003: Recent RCASP valuation
        CARF1004: Reasonable estimate by RCASP
    """

    CARF1001 = "CARF1001"
    CARF1002 = "CARF1002"
    CARF1003 = "CARF1003"
    CARF1004 = "CARF1004"


class CarfCtrlgPersonTypeEnumType(Enum):
    """
    Controlling Person Type.

    Attributes:
        CARF801: CP of legal person - ownership
        CARF802: CP of legal person - other means
        CARF803: CP of legal person - senior managing official
        CARF804: CP of legal arrangement - trust - settlor
        CARF805: CP of legal arrangement - trust - trustee
        CARF806: CP of legal arrangement - trust - protector
        CARF807: CP of legal arrangement - trust - beneficiary
        CARF808: CP of legal arrangement - trust - other
        CARF809: CP of legal arrangement - other - settlor-equivalent
        CARF810: CP of legal arrangement - other - trustee-equivalent
        CARF811: CP of legal arrangement - other - protector-equivalent
        CARF812: CP of legal arrangement - other - beneficiary-
            equivalent
        CARF813: CP of legal arrangement - other - other-equivalent
    """

    CARF801 = "CARF801"
    CARF802 = "CARF802"
    CARF803 = "CARF803"
    CARF804 = "CARF804"
    CARF805 = "CARF805"
    CARF806 = "CARF806"
    CARF807 = "CARF807"
    CARF808 = "CARF808"
    CARF809 = "CARF809"
    CARF810 = "CARF810"
    CARF811 = "CARF811"
    CARF812 = "CARF812"
    CARF813 = "CARF813"


class CarfMessageTypeIndicEnumType(Enum):
    """
    The MessageTypeIndic defines the type of message sent.

    Attributes:
        CARF701: The message contains new information
        CARF702: The message contains corrections/deletions for
            previously sent information. When the MesseageTypeIndic is
            CARF702, the DocTypeIndic can contain either Corrections
            (OECD2) or Deletions (OECD3) or both, but new data (OECD1)
            cannot be contained. Note that OECD0 can be included for
            RCASP's DocTypeIndic.
        CARF703: The message advises there is no data to report
    """

    CARF701 = "CARF701"
    CARF702 = "CARF702"
    CARF703 = "CARF703"


class ExchangeTypeEnumType(Enum):
    """
    Transfer Type.

    Attributes:
        CARF401: Staking
        CARF402: Crypto Loan
        CARF403: Wrapping
        CARF404: Collateral
    """

    CARF401 = "CARF401"
    CARF402 = "CARF402"
    CARF403 = "CARF403"
    CARF404 = "CARF404"


class MessageTypeEnumType(Enum):
    """
    Message type defines the type of reporting.
    """

    CARF = "CARF"


class NexusEnumType(Enum):
    """
    Attributes:
        CARF901: Tax Residence
        CARF902: Incorporation
        CARF903: Management
        CARF904: Place of Business
        CARF905: Branch
        CARF906: Authorisation
        CARF907: Remote Services
    """

    CARF901 = "CARF901"
    CARF902 = "CARF902"
    CARF903 = "CARF903"
    CARF904 = "CARF904"
    CARF905 = "CARF905"
    CARF906 = "CARF906"
    CARF907 = "CARF907"


class OrganisationInTypeIntype(Enum):
    LEI = "LEI"
    EIN = "EIN"
    BRN = "BRN"
    OTHER = "Other"


class TransferOutTypeEnumType(Enum):
    """
    Account Number Type.

    Attributes:
        CARF601: Transfer to another RCASP
        CARF602: Crypto Loan
        CARF603: Purchase of goods or services, to be used in respect of
            transactions other than those already reported as Reportable
            Retail Payment Transactions
        CARF604: Collateral
        CARF605: Other
        CARF606: Unknown (to be selected as the default value where the
            Reporting Crypto-Asset Service Provider has no knowledge on
            the Transfer Type)
    """

    CARF601 = "CARF601"
    CARF602 = "CARF602"
    CARF603 = "CARF603"
    CARF604 = "CARF604"
    CARF605 = "CARF605"
    CARF606 = "CARF606"


class TransferTypeEnumType(Enum):
    """
    Transfer Type.

    Attributes:
        CARF501: Airdrop
        CARF502: Staking income
        CARF503: Mining income
        CARF504: Crpyto loan
        CARF505: Transfer from another RCASP
        CARF506: Sale of goods or services
        CARF507: Collateral
        CARF508: Other
        CARF509: Unknown (to be selected as the default value where the
            Reporting Crypto-Asset Service Provider has no knowledge on
            the Transfer Type)
    """

    CARF501 = "CARF501"
    CARF502 = "CARF502"
    CARF503 = "CARF503"
    CARF504 = "CARF504"
    CARF505 = "CARF505"
    CARF506 = "CARF506"
    CARF507 = "CARF507"
    CARF508 = "CARF508"
    CARF509 = "CARF509"


@dataclass(kw_only=True)
class AddressType:
    class Meta:
        name = "Address_Type"

    country_code: CountryCodeType = field(
        metadata={
            "name": "CountryCode",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    address_fix: AddressFixType = field(
        metadata={
            "name": "AddressFix",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    additional_address_info: None | str = field(
        default=None,
        metadata={
            "name": "AdditionalAddressInfo",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
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
class BirthPlaceType:
    """
    This element provides information about the place of birth.

    This element must be filled in at least with the city and the country
    of birth (either the current jurisdiction identified by 2-characters
    country code or a former jurisdiction identified by a name).
    """

    class Meta:
        name = "BirthPlace_Type"

    city: str = field(
        metadata={
            "name": "City",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        }
    )
    city_subentity: None | str = field(
        default=None,
        metadata={
            "name": "CitySubentity",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    country_info: BirthPlaceType.CountryInfo = field(
        metadata={
            "name": "CountryInfo",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )

    @dataclass(kw_only=True)
    class CountryInfo:
        country_code: None | CountryCodeType = field(
            default=None,
            metadata={
                "name": "CountryCode",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )
        former_country_name: None | str = field(
            default=None,
            metadata={
                "name": "FormerCountryName",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
                "min_length": 1,
                "max_length": 200,
            },
        )


@dataclass(kw_only=True)
class IndividualInType:
    """
    This is the identification number/identification code for the Entity in
    question.

    As the identifier may be not strictly numeric, it is just defined as a
    string of characters. Attribute 'issuedBy' is required to designate the
    issuer of the identifier. Attribute 'INType' defines the type of
    identification number.

    Attributes:
        value:
        issued_by: Country code of issuing country, indicating country
            of Residence (to taxes and other)
    """

    class Meta:
        name = "IndividualIN_Type"

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


@dataclass(kw_only=True)
class MessageSpecType:
    """
    Information in the message header identifies the Tax Administration
    that is sending the message.

    It specifies when the message was created, what period (normally a
    year) the report is for, and the nature of the report (original,
    corrected, supplemental, etc).
    """

    class Meta:
        name = "MessageSpec_Type"

    sending_entity_in: None | str = field(
        default=None,
        metadata={
            "name": "SendingEntityIN",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    transmitting_country: CountryCodeType = field(
        metadata={
            "name": "TransmittingCountry",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    receiving_country: CountryCodeType = field(
        metadata={
            "name": "ReceivingCountry",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    message_type: MessageTypeEnumType = field(
        metadata={
            "name": "MessageType",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    warning: None | str = field(
        default=None,
        metadata={
            "name": "Warning",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    contact: None | str = field(
        default=None,
        metadata={
            "name": "Contact",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    message_ref_id: str = field(
        metadata={
            "name": "MessageRefId",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 170,
        }
    )
    message_type_indic: CarfMessageTypeIndicEnumType = field(
        metadata={
            "name": "MessageTypeIndic",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    reporting_period: XmlDate = field(
        metadata={
            "name": "ReportingPeriod",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    timestamp: XmlDateTime = field(
        metadata={
            "name": "Timestamp",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )


@dataclass(kw_only=True)
class MonAmntType:
    """
    This data type is to be used whenever monetary amounts are to be
    communicated.

    Such amounts shall be given in with full amoutns and two decimals. The
    code for the currency in which the value is expressed has to be taken
    from the ISO codelist 4217 and added in attribute currCode.
    """

    class Meta:
        name = "MonAmnt_Type"

    value: Decimal = field()
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
class NamePersonType:
    """
    The user must spread the data about the name of a party over up to six
    elements.

    The container element for this will be 'NameFix'.
    """

    class Meta:
        name = "NamePerson_Type"

    preceding_title: None | str = field(
        default=None,
        metadata={
            "name": "PrecedingTitle",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    title: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Title",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    first_name: NamePersonType.FirstName = field(
        metadata={
            "name": "FirstName",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    middle_name: list[NamePersonType.MiddleName] = field(
        default_factory=list,
        metadata={
            "name": "MiddleName",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    name_prefix: None | NamePersonType.NamePrefix = field(
        default=None,
        metadata={
            "name": "NamePrefix",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    last_name: NamePersonType.LastName = field(
        metadata={
            "name": "LastName",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    generation_identifier: list[str] = field(
        default_factory=list,
        metadata={
            "name": "GenerationIdentifier",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    suffix: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Suffix",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        },
    )
    general_suffix: None | str = field(
        default=None,
        metadata={
            "name": "GeneralSuffix",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
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
    class FirstName:
        """
        Attributes:
            value:
            xnl_name_type: Defines the name type of FirstName. Example:
                Given Name, Forename, Christian Name, Father's Name,
                etc. In some countries, FirstName could be a Family Name
                or a SurName. Use this attribute to define the type for
                this name.
        """

        value: str = field(
            default="",
            metadata={
                "min_length": 1,
                "max_length": 200,
            },
        )
        xnl_name_type: None | str = field(
            default=None,
            metadata={
                "name": "xnlNameType",
                "type": "Attribute",
                "min_length": 1,
                "max_length": 200,
            },
        )

    @dataclass(kw_only=True)
    class MiddleName:
        """
        Attributes:
            value:
            xnl_name_type: Defines the name type of Middle Name.
                Example: First name, middle name, maiden name, father's
                name, given name, etc.
        """

        value: str = field(
            default="",
            metadata={
                "min_length": 1,
                "max_length": 200,
            },
        )
        xnl_name_type: None | str = field(
            default=None,
            metadata={
                "name": "xnlNameType",
                "type": "Attribute",
                "min_length": 1,
                "max_length": 200,
            },
        )

    @dataclass(kw_only=True)
    class NamePrefix:
        """
        Attributes:
            value:
            xnl_name_type: Defines the type of name associated with the
                NamePrefix. For example the type of name is LastName and
                this prefix is the prefix for this last name.
        """

        value: str = field(
            default="",
            metadata={
                "min_length": 1,
                "max_length": 200,
            },
        )
        xnl_name_type: None | str = field(
            default=None,
            metadata={
                "name": "xnlNameType",
                "type": "Attribute",
                "min_length": 1,
                "max_length": 200,
            },
        )

    @dataclass(kw_only=True)
    class LastName:
        """
        Attributes:
            value:
            xnl_name_type: Defines the name type of LastName. Example:
                Father's name, Family name, Sur Name, Mother's Name,
                etc. In some countries, LastName could be the given name
                or first name.
        """

        value: str = field(
            default="",
            metadata={
                "min_length": 1,
                "max_length": 200,
            },
        )
        xnl_name_type: None | str = field(
            default=None,
            metadata={
                "name": "xnlNameType",
                "type": "Attribute",
                "min_length": 1,
                "max_length": 200,
            },
        )


@dataclass(kw_only=True)
class OrganisationInType:
    """
    This is the identification number/identification code for the Entity in
    question.

    As the identifier may be not strictly numeric, it is just defined as a
    string of characters. Attribute 'issuedBy' is required to designate the
    issuer of the identifier. Attribute 'INType' defines the type of
    identification number.

    Attributes:
        value:
        issued_by: Country code of issuing country, indicating country
            of Residence (to taxes and other)
        intype: Identification Number Type
    """

    class Meta:
        name = "OrganisationIN_Type"

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
    intype: None | OrganisationInTypeIntype = field(
        default=None,
        metadata={
            "name": "INType",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class TinType:
    class Meta:
        name = "TIN_Type"

    value: str = field(
        default="",
        metadata={
            "min_length": 0,
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
    unknown: None | bool = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class OrganisationPartyType:
    """
    Attributes:
        res_country_code:
        tin:
        in_value: Entity Identification Number - OrganisationIN_Type
        iin: Individual Identification Number - IndividualIN_Type
        name:
        address:
    """

    class Meta:
        name = "OrganisationParty_Type"

    res_country_code: list[CountryCodeType] = field(
        default_factory=list,
        metadata={
            "name": "ResCountryCode",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_occurs": 1,
        },
    )
    tin: list[TinType] = field(
        default_factory=list,
        metadata={
            "name": "TIN",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_occurs": 1,
        },
    )
    in_value: list[OrganisationInType] = field(
        default_factory=list,
        metadata={
            "name": "IN",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    iin: list[IndividualInType] = field(
        default_factory=list,
        metadata={
            "name": "IIN",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    name: list[NameOrganisationType] = field(
        default_factory=list,
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_occurs": 1,
        },
    )
    address: list[AddressType] = field(
        default_factory=list,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_occurs": 1,
        },
    )


@dataclass(kw_only=True)
class PersonPartyType:
    """
    Attributes:
        res_country_code:
        tin:
        iin: Individual Identification Number
        name:
        address:
        nationality:
        birth_info: .
    """

    class Meta:
        name = "PersonParty_Type"

    res_country_code: list[CountryCodeType] = field(
        default_factory=list,
        metadata={
            "name": "ResCountryCode",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_occurs": 1,
        },
    )
    tin: list[TinType] = field(
        default_factory=list,
        metadata={
            "name": "TIN",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_occurs": 1,
        },
    )
    iin: list[IndividualInType] = field(
        default_factory=list,
        metadata={
            "name": "IIN",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    name: list[NamePersonType] = field(
        default_factory=list,
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_occurs": 1,
        },
    )
    address: list[AddressType] = field(
        default_factory=list,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_occurs": 1,
        },
    )
    nationality: list[CountryCodeType] = field(
        default_factory=list,
        metadata={
            "name": "Nationality",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    birth_info: PersonPartyType.BirthInfo = field(
        metadata={
            "name": "BirthInfo",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )

    @dataclass(kw_only=True)
    class BirthInfo:
        birth_date: XmlDate = field(
            metadata={
                "name": "BirthDate",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        birth_place: None | BirthPlaceType = field(
            default=None,
            metadata={
                "name": "BirthPlace",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )


@dataclass(kw_only=True)
class RelevantTransactionsType:
    """
    Attributes:
        crypto_asset:
        crypto_to_crypto_in:
        crypto_to_crypto_out:
        crypto_fiat_in:
        crypto_fiat_out:
        crypto_transfer_in:
        crypto_transfer_out:
        transfer_wallet:
        rrpt: Reportable Retail Payment Transcactions (Relevant Crypto
            Assets)
    """

    class Meta:
        name = "RelevantTransactions_Type"

    crypto_asset: str = field(
        metadata={
            "name": "CryptoAsset",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_length": 1,
            "max_length": 200,
        }
    )
    crypto_to_crypto_in: list[RelevantTransactionsType.CryptoToCryptoIn] = (
        field(
            default_factory=list,
            metadata={
                "name": "CryptoToCryptoIn",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )
    )
    crypto_to_crypto_out: list[RelevantTransactionsType.CryptoToCryptoOut] = (
        field(
            default_factory=list,
            metadata={
                "name": "CryptoToCryptoOut",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )
    )
    crypto_fiat_in: list[RelevantTransactionsType.CryptoFiatIn] = field(
        default_factory=list,
        metadata={
            "name": "CryptoFiatIn",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    crypto_fiat_out: list[RelevantTransactionsType.CryptoFiatOut] = field(
        default_factory=list,
        metadata={
            "name": "CryptoFiatOut",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    crypto_transfer_in: list[RelevantTransactionsType.CryptoTransferIn] = (
        field(
            default_factory=list,
            metadata={
                "name": "CryptoTransferIn",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )
    )
    crypto_transfer_out: list[RelevantTransactionsType.CryptoTransferOut] = (
        field(
            default_factory=list,
            metadata={
                "name": "CryptoTransferOut",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )
    )
    transfer_wallet: list[RelevantTransactionsType.TransferWallet] = field(
        default_factory=list,
        metadata={
            "name": "TransferWallet",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    rrpt: list[RelevantTransactionsType.Rrpt] = field(
        default_factory=list,
        metadata={
            "name": "RRPT",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )

    @dataclass(kw_only=True)
    class CryptoToCryptoIn:
        exchange_type: None | ExchangeTypeEnumType = field(
            default=None,
            metadata={
                "name": "ExchangeType",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )
        numberof_transactions: int = field(
            metadata={
                "name": "NumberofTransactions",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        amount: MonAmntType = field(
            metadata={
                "name": "Amount",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        numberof_units: Decimal = field(
            metadata={
                "name": "NumberofUnits",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )

    @dataclass(kw_only=True)
    class CryptoToCryptoOut:
        exchange_type: None | ExchangeTypeEnumType = field(
            default=None,
            metadata={
                "name": "ExchangeType",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )
        numberof_transactions: int = field(
            metadata={
                "name": "NumberofTransactions",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        amount: MonAmntType = field(
            metadata={
                "name": "Amount",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        numberof_units: Decimal = field(
            metadata={
                "name": "NumberofUnits",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )

    @dataclass(kw_only=True)
    class CryptoFiatIn:
        exchange_type: None | ExchangeTypeEnumType = field(
            default=None,
            metadata={
                "name": "ExchangeType",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )
        numberof_transactions: int = field(
            metadata={
                "name": "NumberofTransactions",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        amount: MonAmntType = field(
            metadata={
                "name": "Amount",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        numberof_units: Decimal = field(
            metadata={
                "name": "NumberofUnits",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )

    @dataclass(kw_only=True)
    class CryptoFiatOut:
        exchange_type: None | ExchangeTypeEnumType = field(
            default=None,
            metadata={
                "name": "ExchangeType",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )
        numberof_transactions: int = field(
            metadata={
                "name": "NumberofTransactions",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        amount: MonAmntType = field(
            metadata={
                "name": "Amount",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        numberof_units: Decimal = field(
            metadata={
                "name": "NumberofUnits",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )

    @dataclass(kw_only=True)
    class CryptoTransferIn:
        transfer_type: TransferTypeEnumType = field(
            metadata={
                "name": "TransferType",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        numberof_transactions: int = field(
            metadata={
                "name": "NumberofTransactions",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        amount: MonAmntType = field(
            metadata={
                "name": "Amount",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        numberof_units: Decimal = field(
            metadata={
                "name": "NumberofUnits",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        alt_valuation: None | AltValuationEnumType = field(
            default=None,
            metadata={
                "name": "AltValuation",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )

    @dataclass(kw_only=True)
    class CryptoTransferOut:
        transfer_type: TransferOutTypeEnumType = field(
            metadata={
                "name": "TransferType",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        numberof_transactions: int = field(
            metadata={
                "name": "NumberofTransactions",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        amount: MonAmntType = field(
            metadata={
                "name": "Amount",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        numberof_units: Decimal = field(
            metadata={
                "name": "NumberofUnits",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        alt_valuation: None | AltValuationEnumType = field(
            default=None,
            metadata={
                "name": "AltValuation",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )

    @dataclass(kw_only=True)
    class TransferWallet:
        amount: MonAmntType = field(
            metadata={
                "name": "Amount",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        numberof_units: Decimal = field(
            metadata={
                "name": "NumberofUnits",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        alt_valuation: None | AltValuationEnumType = field(
            default=None,
            metadata={
                "name": "AltValuation",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )

    @dataclass(kw_only=True)
    class Rrpt:
        numberof_transactions: int = field(
            metadata={
                "name": "NumberofTransactions",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        amount: MonAmntType = field(
            metadata={
                "name": "Amount",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )
        numberof_units: Decimal = field(
            metadata={
                "name": "NumberofUnits",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            }
        )


@dataclass(kw_only=True)
class ControllingPersonType:
    class Meta:
        name = "ControllingPerson_Type"

    individual: PersonPartyType = field(
        metadata={
            "name": "Individual",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    ctrlg_person_type: list[CarfCtrlgPersonTypeEnumType] = field(
        default_factory=list,
        metadata={
            "name": "CtrlgPersonType",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_occurs": 1,
        },
    )


@dataclass(kw_only=True)
class IdentityType:
    class Meta:
        name = "Identity_Type"

    individual: None | PersonPartyType = field(
        default=None,
        metadata={
            "name": "Individual",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    entity: None | OrganisationPartyType = field(
        default=None,
        metadata={
            "name": "Entity",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )


@dataclass(kw_only=True)
class RcaspType:
    class Meta:
        name = "RCASP_Type"

    rcasp_id: RcaspType.RcaspId = field(
        metadata={
            "name": "RCASP_ID",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    nexus: None | NexusEnumType = field(
        default=None,
        metadata={
            "name": "Nexus",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    other_nexus: None | RcaspType.OtherNexus = field(
        default=None,
        metadata={
            "name": "OtherNexus",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    doc_spec: DocSpecType = field(
        metadata={
            "name": "DocSpec",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )

    @dataclass(kw_only=True)
    class RcaspId:
        individual: None | PersonPartyType = field(
            default=None,
            metadata={
                "name": "Individual",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )
        entity: None | OrganisationPartyType = field(
            default=None,
            metadata={
                "name": "Entity",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )

    @dataclass(kw_only=True)
    class OtherNexus:
        nexus: NexusEnumType = field(
            metadata={
                "name": "Nexus",
                "type": "Attribute",
            }
        )
        res_country_code: CountryCodeType = field(
            metadata={
                "name": "ResCountryCode",
                "type": "Attribute",
            }
        )


@dataclass(kw_only=True)
class CryptoUsersType:
    class Meta:
        name = "CryptoUsers_Type"

    user_id: CryptoUsersType.UserId = field(
        metadata={
            "name": "UserID",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    controlling_person: list[ControllingPersonType] = field(
        default_factory=list,
        metadata={
            "name": "ControllingPerson",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )
    relevant_transactions: list[RelevantTransactionsType] = field(
        default_factory=list,
        metadata={
            "name": "RelevantTransactions",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
            "min_occurs": 1,
        },
    )
    doc_spec: DocSpecType = field(
        metadata={
            "name": "DocSpec",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )

    @dataclass(kw_only=True)
    class UserId:
        individual: None | PersonPartyType = field(
            default=None,
            metadata={
                "name": "Individual",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )
        entity: None | OrganisationPartyType = field(
            default=None,
            metadata={
                "name": "Entity",
                "type": "Element",
                "namespace": "urn:oecd:ties:carf:v1",
            },
        )


@dataclass(kw_only=True)
class CarfbodyType:
    class Meta:
        name = "CARFBody_Type"

    rcasp: RcaspType = field(
        metadata={
            "name": "RCASP",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        }
    )
    crypto_users: list[CryptoUsersType] = field(
        default_factory=list,
        metadata={
            "name": "CryptoUsers",
            "type": "Element",
            "namespace": "urn:oecd:ties:carf:v1",
        },
    )


@dataclass(kw_only=True)
class CarfOecd:
    """
    Attributes:
        message_spec:
        carfbody:
        version: CARF Version
    """

    class Meta:
        name = "CARF_OECD"
        namespace = "urn:oecd:ties:carf:v1"

    message_spec: MessageSpecType = field(
        metadata={
            "name": "MessageSpec",
            "type": "Element",
        }
    )
    carfbody: list[CarfbodyType] = field(
        default_factory=list,
        metadata={
            "name": "CARFBody",
            "type": "Element",
        },
    )
    version: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 10,
        },
    )
