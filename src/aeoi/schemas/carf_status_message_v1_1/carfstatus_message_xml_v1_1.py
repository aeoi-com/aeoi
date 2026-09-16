from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from xsdata.models.datatype import XmlDate, XmlDateTime

from aeoi.schemas.carf_status_message_v1_1.isocsmtypes_v1_1 import (
    CountryCodeType,
    LanguageCodeType,
)

__NAMESPACE__ = "urn:oecd:ties:csm:v2"


class CarfmessageTypeIndicEnumType(Enum):
    """
    The MessageTypeIndic is currently not used for CARF Status message (for
    future use).
    """

    CARFMESSAGE_STATUS = "CARFMessageStatus"


class FileAcceptanceStatusEnumType(Enum):
    """
    File acceptance status: if the file was accepted or rejected by the
    receiver.

    Attributes:
        ACCEPTED: The file was accepted by the receiver
        REJECTED: The file was rejected by the receiver
    """

    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


@dataclass(kw_only=True)
class FileMetaDataType:
    """
    Attributes:
        ctstransmission_id: CTS Transmission ID assigned to the original
            transmission by CTS when it was initially received
        ctssending_time_stamp: The date and time the original
            transmission was initially delivered to the Receiver by CTS
        uncompressed_file_size_kbqty: Uncompressed File size (KB)
    """

    class Meta:
        name = "FileMetaData_Type"

    ctstransmission_id: None | str = field(
        default=None,
        metadata={
            "name": "CTSTransmissionID",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
            "min_length": 1,
            "max_length": 200,
        },
    )
    ctssending_time_stamp: None | XmlDateTime = field(
        default=None,
        metadata={
            "name": "CTSSendingTimeStamp",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        },
    )
    uncompressed_file_size_kbqty: None | int = field(
        default=None,
        metadata={
            "name": "UncompressedFileSizeKBQty",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        },
    )


class MessageTypeEnumType(Enum):
    """
    Message type defines the type of reporting.
    """

    CARFMESSAGE_STATUS = "CARFMessageStatus"


@dataclass(kw_only=True)
class ErrorDetailType:
    """
    Error message provide more details about the error.
    """

    class Meta:
        name = "ErrorDetail_Type"

    value: str = field(
        default="",
        metadata={
            "min_length": 1,
            "max_length": 4000,
        },
    )
    language: None | LanguageCodeType = field(
        default=None,
        metadata={
            "name": "Language",
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

    Attributes:
        sending_company_in:
        transmitting_country:
        receiving_country:
        message_type:
        warning: Free text expressing the restrictions for use of the
            information this message contains and the legal framework
            under which it is given
        contact: All necessary contact information about persons
            responsible for and involved in the processing of the data
            transmitted in this message, both legally and technically.
            Free text as this is not intended for automatic processing.
        message_ref_id: Unique identifier for this CARF Status message
        message_type_indic: Not used for CARF Status message
        corr_message_ref_id: Not used for CARF Status message
        reporting_period: Not used for CARF Status message
        timestamp:
    """

    class Meta:
        name = "MessageSpec_Type"

    sending_company_in: None | str = field(
        default=None,
        metadata={
            "name": "SendingCompanyIN",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
            "min_length": 1,
            "max_length": 200,
        },
    )
    transmitting_country: CountryCodeType = field(
        metadata={
            "name": "TransmittingCountry",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        }
    )
    receiving_country: CountryCodeType = field(
        metadata={
            "name": "ReceivingCountry",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        }
    )
    message_type: MessageTypeEnumType = field(
        metadata={
            "name": "MessageType",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        }
    )
    warning: None | str = field(
        default=None,
        metadata={
            "name": "Warning",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    contact: None | str = field(
        default=None,
        metadata={
            "name": "Contact",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
            "min_length": 1,
            "max_length": 4000,
        },
    )
    message_ref_id: str = field(
        metadata={
            "name": "MessageRefId",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
            "min_length": 1,
            "max_length": 170,
        }
    )
    message_type_indic: None | CarfmessageTypeIndicEnumType = field(
        default=None,
        metadata={
            "name": "MessageTypeIndic",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        },
    )
    corr_message_ref_id: list[str] = field(
        default_factory=list,
        metadata={
            "name": "CorrMessageRefId",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
            "min_length": 1,
            "max_length": 170,
        },
    )
    reporting_period: None | XmlDate = field(
        default=None,
        metadata={
            "name": "ReportingPeriod",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        },
    )
    timestamp: XmlDateTime = field(
        metadata={
            "name": "Timestamp",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        }
    )


@dataclass(kw_only=True)
class OriginalMessageType:
    """
    Attributes:
        original_message_ref_id: The MessageRefID of the original CARF
            message for which the Status Message is provided
        file_meta_data:
    """

    class Meta:
        name = "OriginalMessage_Type"

    original_message_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "OriginalMessageRefID",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
            "min_length": 1,
            "max_length": 170,
        },
    )
    file_meta_data: None | FileMetaDataType = field(
        default=None,
        metadata={
            "name": "FileMetaData",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        },
    )


@dataclass(kw_only=True)
class ValidationResultType:
    """
    Attributes:
        status: Indicate if the file was accepted or rejected by the
            receiver
        validated_by: Indicate the version of the validation tool that
            was used to generate this Status Message
    """

    class Meta:
        name = "ValidationResult_Type"

    status: FileAcceptanceStatusEnumType = field(
        metadata={
            "name": "Status",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        }
    )
    validated_by: list[str] = field(
        default_factory=list,
        metadata={
            "name": "ValidatedBy",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
            "min_occurs": 1,
            "min_length": 1,
            "max_length": 400,
        },
    )


@dataclass(kw_only=True)
class FileErrorType:
    """
    Attributes:
        code: Error Code
        details: Error Details
    """

    class Meta:
        name = "FileError_Type"

    code: str = field(
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
            "min_length": 1,
            "max_length": 10,
        }
    )
    details: None | ErrorDetailType = field(
        default=None,
        metadata={
            "name": "Details",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        },
    )


@dataclass(kw_only=True)
class RecordErrorType:
    """
    Attributes:
        code: Error Code
        details: Error Details
        doc_ref_idin_error: DocRefID of the record causing the error
        fields_in_error: Information on the fields causing the error
    """

    class Meta:
        name = "RecordError_Type"

    code: str = field(
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
            "min_length": 1,
            "max_length": 10,
        }
    )
    details: None | ErrorDetailType = field(
        default=None,
        metadata={
            "name": "Details",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        },
    )
    doc_ref_idin_error: list[str] = field(
        default_factory=list,
        metadata={
            "name": "DocRefIDInError",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
            "min_length": 1,
            "max_length": 200,
        },
    )
    fields_in_error: list[RecordErrorType.FieldsInError] = field(
        default_factory=list,
        metadata={
            "name": "FieldsInError",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        },
    )

    @dataclass(kw_only=True)
    class FieldsInError:
        field_path: str = field(
            metadata={
                "name": "FieldPath",
                "type": "Element",
                "namespace": "urn:oecd:ties:csm:v2",
                "min_length": 1,
                "max_length": 400,
            }
        )


@dataclass(kw_only=True)
class ValidationErrorsType:
    class Meta:
        name = "ValidationErrors_Type"

    file_error: list[FileErrorType] = field(
        default_factory=list,
        metadata={
            "name": "FileError",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        },
    )
    record_error: list[RecordErrorType] = field(
        default_factory=list,
        metadata={
            "name": "RecordError",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        },
    )


@dataclass(kw_only=True)
class CarfmessageStatusType:
    class Meta:
        name = "CARFMessageStatus_Type"

    original_message: OriginalMessageType = field(
        metadata={
            "name": "OriginalMessage",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        }
    )
    validation_errors: ValidationErrorsType = field(
        metadata={
            "name": "ValidationErrors",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        }
    )
    validation_result: ValidationResultType = field(
        metadata={
            "name": "ValidationResult",
            "type": "Element",
            "namespace": "urn:oecd:ties:csm:v2",
        }
    )


@dataclass(kw_only=True)
class CarfstatusMessageOecd:
    """
    Attributes:
        message_spec:
        carfstatus_message:
        version: CARF Status Message Version
    """

    class Meta:
        name = "CARFStatusMessage_OECD"
        namespace = "urn:oecd:ties:csm:v2"

    message_spec: MessageSpecType = field(
        metadata={
            "name": "MessageSpec",
            "type": "Element",
        }
    )
    carfstatus_message: CarfmessageStatusType = field(
        metadata={
            "name": "CARFStatusMessage",
            "type": "Element",
        }
    )
    version: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_length": 1,
            "max_length": 10,
        },
    )
