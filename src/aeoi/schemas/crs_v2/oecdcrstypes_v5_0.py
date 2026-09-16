from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

__NAMESPACE__ = "urn:oecd:ties:crsstf:v5"


class OecddocTypeIndicEnumType(Enum):
    """
    This element specifies the type of data being submitted.

    Attributes:
        OECD0: Resend Data
        OECD1: New Data
        OECD2: Corrected Data
        OECD3: Deletion of Data
        OECD10: Resend Test Data
        OECD11: New Test Data
        OECD12: Corrected Test Data
        OECD13: Deletion of Test Data
    """

    OECD0 = "OECD0"
    OECD1 = "OECD1"
    OECD2 = "OECD2"
    OECD3 = "OECD3"
    OECD10 = "OECD10"
    OECD11 = "OECD11"
    OECD12 = "OECD12"
    OECD13 = "OECD13"


class OecdlegalAddressTypeEnumType(Enum):
    """
    This is a datatype for an attribute to an address.

    It serves to indicate the legal character of that address (residential,
    business etc.).

    Attributes:
        OECD301: residentialOrBusiness
        OECD302: residential
        OECD303: business
        OECD304: registeredOffice
        OECD305: unspecified
    """

    OECD301 = "OECD301"
    OECD302 = "OECD302"
    OECD303 = "OECD303"
    OECD304 = "OECD304"
    OECD305 = "OECD305"


class OecdnameTypeEnumType(Enum):
    """
    It is possible for stf documents to contain several names for the same
    party.

    This is a qualifier to indicate the type of a particular name. Such
    types include nicknames ('nick'), names under which a party does
    business ('dba' a short name for the entity, or a name that is used for
    public acquaintance instead of the official business name) etc.

    Attributes:
        OECD201: SMFAliasOrOther
        OECD202: indiv (individual)
        OECD203: alias (alias)
        OECD204: nick (nickname)
        OECD205: aka (also known as)
        OECD206: dba (doing business as)
        OECD207: legal (legal name)
        OECD208: atbirth (name at birth)
    """

    OECD201 = "OECD201"
    OECD202 = "OECD202"
    OECD203 = "OECD203"
    OECD204 = "OECD204"
    OECD205 = "OECD205"
    OECD206 = "OECD206"
    OECD207 = "OECD207"
    OECD208 = "OECD208"


@dataclass(kw_only=True)
class DocSpecType:
    """
    Document specification: Data identifying and describing the document,
    where 'document' here means the part of a message that is to transmit
    the data about a single block of CRS information.

    Attributes:
        doc_type_indic:
        doc_ref_id: Sender's unique identifier of this document
        corr_message_ref_id: Reference id of the message of the document
            referred to if this is a correction
        corr_doc_ref_id: Reference id of the document referred to if
            this is correction
    """

    class Meta:
        name = "DocSpec_Type"

    doc_type_indic: OecddocTypeIndicEnumType = field(
        metadata={
            "name": "DocTypeIndic",
            "type": "Element",
            "namespace": "urn:oecd:ties:crsstf:v5",
        }
    )
    doc_ref_id: str = field(
        metadata={
            "name": "DocRefId",
            "type": "Element",
            "namespace": "urn:oecd:ties:crsstf:v5",
            "min_length": 1,
            "max_length": 200,
        }
    )
    corr_message_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "CorrMessageRefId",
            "type": "Element",
            "namespace": "urn:oecd:ties:crsstf:v5",
            "min_length": 1,
            "max_length": 170,
        },
    )
    corr_doc_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "CorrDocRefId",
            "type": "Element",
            "namespace": "urn:oecd:ties:crsstf:v5",
            "min_length": 1,
            "max_length": 200,
        },
    )
