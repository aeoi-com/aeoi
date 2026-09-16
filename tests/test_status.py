"""Status message parsing: OECD CRS Status Message XML 2.0 and portal text."""

from pathlib import Path

import xmlschema
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.models.datatype import XmlDateTime

import aeoi.schemas.crs_status_message_v2.crs_status_message_xml_v2_0 as m
from aeoi.estv import status

ROOT = Path(__file__).resolve().parents[1]
NS = {"csm": "urn:oecd:ties:csm:v2", "stf": "urn:oecd:ties:crsstf:v5"}


def _status_xml(accepted: bool) -> str:
    """A synthetic ESTV-style status message, valid against the OECD schema."""
    errors = m.ValidationErrorsType()  # mandatory element, empty when accepted
    if not accepted:
        errors = m.ValidationErrorsType(
            record_error=[
                m.RecordErrorType(
                    code="60002",
                    details=m.ErrorDetailType(
                        value="AccountBalance darf keinen negativen Wert enthalten"
                    ),
                    doc_ref_idin_error=["CH2026CHabc-1"],
                    fields_in_error=[
                        m.RecordErrorType.FieldsInError(field_path="AccountReport/AccountBalance")
                    ],
                ),
                m.RecordErrorType(code="98200", doc_ref_idin_error=["CH2026CHabc-2"]),
            ]
        )
    doc = m.CrsstatusMessageOecd(
        message_spec=m.MessageSpecType(
            transmitting_country=m.CountryCodeType("CH"),
            receiving_country=m.CountryCodeType("CH"),
            message_type=m.MessageTypeEnumType("CRSMessageStatus"),
            message_ref_id="CH2026CHstatus-1",
            timestamp=XmlDateTime(2027, 5, 2, 9, 0, 0),
        ),
        crs_status_message=m.CrsMessageStatusType(
            original_message=m.OriginalMessageType(original_message_ref_id="CH2026CHorig-1"),
            validation_errors=errors,
            validation_result=m.ValidationResultType(
                status=m.FileAcceptanceStatusEnumType("Accepted" if accepted else "Rejected"),
                validated_by=["ESTV"],
            ),
        ),
    )
    return XmlSerializer(config=SerializerConfig(indent="  ")).render(doc, ns_map=NS)


def test_synthetic_status_messages_are_schema_valid():
    schema = xmlschema.XMLSchema(
        ROOT / "schemas" / "crs_status_message_v2.0" / "CrsStatusMessageXML_v2.0.xsd"
    )
    for accepted in (True, False):
        errors = [e.reason for e in schema.iter_errors(_status_xml(accepted))]
        assert not errors, errors


def test_parse_rejected_status_message():
    out = status.parse_status_message(_status_xml(False))
    assert out.accepted is False and out.original_message_ref_id == "CH2026CHorig-1"
    assert out.codes == ["60002", "98200"]
    first = out.findings[0]
    assert first.doc_ref_ids == ("CH2026CHabc-1",)
    assert first.fields == ("AccountReport/AccountBalance",)
    assert first.rule["status"] == "implemented" and "5.3.7" in first.rule["section"]
    assert [f.code for f in out.should_have_been_caught()] == ["60002", "98200"]
    text = status.render(out)
    assert "REJECTED" in text and "60002 (5.3.7" in text and "report them as bugs" in text


def test_parse_accepted_status_message():
    out = status.parse_status_message(_status_xml(True))
    assert out.accepted is True and out.findings == []
    assert status.render(out).startswith("ACCEPTED")


def test_parse_portal_text():
    text = """Meldung CH2026CH8b0f7048-e2ff-11e6-bf01-fe55135034f3
    Fehlerbericht
    80002 CorrDocRefId unbekannt - CH2026CHc0e1a474-558a-414d-82e1-5ba5811cb936
    Fehlercode 98003: FI nicht angemeldet
    """
    out = status.parse_text(text)
    assert out.accepted is False
    assert out.original_message_ref_id == "CH2026CH8b0f7048-e2ff-11e6-bf01-fe55135034f3"
    assert out.codes == ["80002", "98003"]
    assert out.findings[0].doc_ref_ids == ("CH2026CHc0e1a474-558a-414d-82e1-5ba5811cb936",)
    assert out.findings[0].rule["status"] == "registry"
    assert out.findings[1].rule["status"] == "portal"
    assert not out.should_have_been_caught()


def test_parse_portal_text_accepted():
    out = status.parse_text("Validierungsbestätigung für CH2026CHabc\nAlles akzeptiert")
    assert out.accepted is True and out.findings == []
