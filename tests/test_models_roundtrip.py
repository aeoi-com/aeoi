"""The generated models must read the ESTV annex examples and write them back as valid XML."""

from pathlib import Path

import pytest
import xmlschema
from lxml import etree
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
CRS3 = "urn:oecd:ties:crs:v3"


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


def test_serializer_writes_utf8_without_numeric_references():
    """'&#' is a forbidden sequence for the ESTV (Anhang 7.2): non-ASCII must be raw UTF-8."""
    doc = XmlParser().parse(ROOT / "tests" / "corpus" / "estv_v2" / "neumeldung.xml", CrsOecd2)
    out = XmlSerializer(config=SerializerConfig(encoding="UTF-8")).render(doc, ns_map=NS_V2)
    assert "Zürich" in out and "&#" not in out
    assert out.startswith('<?xml version="1.0" encoding="UTF-8"?>')


# --- CRS 3.0: what is new and mandatory, established by construction --------------------


def _to_v3(path: Path) -> etree._ElementTree:
    """Upgrade an ESTV 2.0 example to a complete, valid 3.0 document.

    Adds exactly the elements the 3.0 schema makes mandatory, at the position the sequences
    require: SelfCert before the Individual/Organisation choice in AccountHolder; CtrlgPersonType
    (now 1..n) and SelfCert (last) in ControllingPerson; DDProcedure and AccountType after Payment
    in AccountReport.
    """
    raw = path.read_text(encoding="utf-8").replace("urn:oecd:ties:crs:v2", CRS3)
    tree = etree.ElementTree(etree.fromstring(raw.encode("utf-8")))
    root = tree.getroot()
    root.set("version", "3.0")
    q = lambda tag: f"{{{CRS3}}}{tag}"
    for holder in root.iter(q("AccountHolder")):
        self_cert = etree.Element(q("SelfCert"))
        self_cert.text = "CRS901"
        holder.insert(0, self_cert)  # after any EquityInterestType (none here), before the choice
    for cp in root.iter(q("ControllingPerson")):
        if cp.find(q("CtrlgPersonType")) is None:
            t = etree.SubElement(cp, q("CtrlgPersonType"))
            t.text = "CRS801"
        sc = etree.SubElement(cp, q("SelfCert"))
        sc.text = "CRS1001"
    for report in root.iter(q("AccountReport")):
        anchor = report.findall(q("Payment"))[-1:] or [report.find(q("AccountBalance"))]
        idx = list(report).index(anchor[0]) + 1
        dd = etree.Element(q("DDProcedure"))
        dd.text = "CRS1201"
        at = etree.Element(q("AccountType"))
        at.text = "CRS1101"
        report.insert(idx, dd)
        report.insert(idx + 1, at)
    return tree


def _remove_all(tree: etree._ElementTree, tag: str) -> etree._ElementTree:
    copy = etree.ElementTree(etree.fromstring(etree.tostring(tree)))
    for el in list(copy.getroot().iter(f"{{{CRS3}}}{tag}")):
        el.getparent().remove(el)
    return copy


def test_upgraded_example_is_valid_v3(schema_v3):
    tree = _to_v3(ROOT / "tests" / "corpus" / "estv_v2" / "neumeldung.xml")
    errors = [e.reason for e in schema_v3.iter_errors(etree.tostring(tree))]
    assert not errors, errors


@pytest.mark.parametrize("tag", ["SelfCert", "DDProcedure", "AccountType", "CtrlgPersonType"])
def test_v3_mandatory_elements(schema_v3, tag):
    """Removing any of these from a valid 3.0 document makes it invalid (new in 3.0 vs 2.0)."""
    tree = _to_v3(ROOT / "tests" / "corpus" / "estv_v2" / "neumeldung.xml")
    stripped = _remove_all(tree, tag)
    reasons = [e.reason or "" for e in schema_v3.iter_errors(etree.tostring(stripped))]
    assert reasons and any(tag in r for r in reasons), reasons


@pytest.mark.parametrize("tag", ["JointAccount", "EquityInterestType"])
def test_v3_optional_elements_absent_is_fine(schema_v3, tag):
    tree = _to_v3(ROOT / "tests" / "corpus" / "estv_v2" / "neumeldung.xml")
    assert tree.getroot().find(f".//{{{CRS3}}}{tag}") is None
    assert schema_v3.is_valid(etree.tostring(tree))


def test_v3_element_order_inside_controlling_person_and_holder(schema_v3):
    """SelfCert is the LAST child of ControllingPerson and precedes the party choice in AccountHolder."""
    tree = _to_v3(ROOT / "tests" / "corpus" / "estv_v2" / "neumeldung.xml")
    q = lambda tag: f"{{{CRS3}}}{tag}"
    cp = tree.getroot().find(f".//{q('ControllingPerson')}")
    assert [etree.QName(c).localname for c in cp] == ["Individual", "CtrlgPersonType", "SelfCert"]
    holder = tree.getroot().find(f".//{q('AccountHolder')}")
    names = [etree.QName(c).localname for c in holder]
    assert names[0] == "SelfCert" and names[1] in ("Individual", "Organisation")
    # and the schema rejects SelfCert placed first in ControllingPerson
    wrong = etree.ElementTree(etree.fromstring(etree.tostring(tree)))
    cp = wrong.getroot().find(f".//{q('ControllingPerson')}")
    sc = cp.find(q("SelfCert"))
    cp.remove(sc)
    cp.insert(0, sc)
    assert not schema_v3.is_valid(etree.tostring(wrong))
