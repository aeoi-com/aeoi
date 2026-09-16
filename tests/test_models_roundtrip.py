"""The generated models must read the ESTV annex examples and write them back as valid XML."""

from pathlib import Path

import pytest
import xmlschema
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from aeoi.schemas.crs_v2.crs_xml_v2_0 import CrsOecd as CrsOecd2

ROOT = Path(__file__).resolve().parents[1]
CORPUS = sorted((ROOT / "tests" / "corpus" / "estv_v2").glob("*.xml"))
NS_V2 = {
    "crs": "urn:oecd:ties:crs:v2",
    "cfc": "urn:oecd:ties:commontypesfatcacrs:v2",
    "stf": "urn:oecd:ties:crsstf:v5",
}


@pytest.fixture(scope="module")
def schema_v2():
    return xmlschema.XMLSchema(ROOT / "schemas" / "crs_v2.0" / "CrsXML_v2.0.xsd")


@pytest.fixture(scope="module")
def schema_v3():
    return xmlschema.XMLSchema(ROOT / "schemas" / "crs_v3.0" / "CrsXML_v3.0.xsd")


@pytest.mark.parametrize("path", CORPUS, ids=[p.stem for p in CORPUS])
def test_estv_examples_are_valid_v2(path, schema_v2):
    assert schema_v2.is_valid(path)


@pytest.mark.parametrize("path", CORPUS, ids=[p.stem for p in CORPUS])
def test_model_round_trip_stays_valid(path, schema_v2):
    doc = XmlParser().parse(path, CrsOecd2)
    out = XmlSerializer(config=SerializerConfig(indent="  ")).render(doc, ns_map=NS_V2)
    errors = [str(e).splitlines()[0] for e in schema_v2.iter_errors(out)]
    assert not errors, errors


def test_address_fix_precedes_address_free(schema_v2):
    """Regression for the xsdata field-order patch (tools/generate_models.py)."""
    doc = XmlParser().parse(ROOT / "tests" / "corpus" / "estv_v2" / "neumeldung.xml", CrsOecd2)
    address = doc.crs_body[0].reporting_fi.address[0]
    assert address.address_fix is not None and address.address_free is not None
    out = XmlSerializer().render(doc, ns_map=NS_V2)
    assert out.index("AddressFix") < out.index("AddressFree")


def test_v3_makes_self_cert_and_dd_procedure_mandatory(schema_v3):
    """Documented finding: a 2.0 document renamed to 3.0 fails exactly on the new mandatory elements."""
    raw = (ROOT / "tests" / "corpus" / "estv_v2" / "neumeldung.xml").read_text(encoding="utf-8")
    v3 = raw.replace("urn:oecd:ties:crs:v2", "urn:oecd:ties:crs:v3").replace(
        'version="2.0"', 'version="3.0"'
    )

    reasons = " ".join((e.reason or "") for e in schema_v3.iter_errors(v3))
    assert "SelfCert" in reasons and "DDProcedure" in reasons
