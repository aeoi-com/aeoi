"""ESTV rules the builder satisfies by construction (Technische Wegleitung 5.3.1-5.3.6, 5.3.11).

Each assertion names the ESTV code it covers so the rules catalogue can prove coverage.
"""

import datetime as dt

from lxml import etree

from aeoi.crs import build
from aeoi.crs.example import sample_message
from aeoi.estv import packaging

NS = {"crs": "urn:oecd:ties:crs:v3", "stf": "urn:oecd:ties:crsstf:v5"}


def _root(version="3.0", **kw):
    return etree.fromstring(build.build(sample_message(), version, **kw).xml.encode())


def test_message_header_by_construction():
    now = dt.datetime(2027, 4, 2, 8, 0, tzinfo=dt.UTC)
    root = _root(now=now)
    spec = root.find("crs:MessageSpec", NS)
    assert root.get("version") == "3.0"  # 98000 version attribute present and supported
    assert spec.findtext("crs:TransmittingCountry", namespaces=NS) == "CH"  # 98002
    assert spec.findtext("crs:ReceivingCountry", namespaces=NS) == "CH"  # 50012
    assert spec.findtext("crs:ReportingPeriod", namespaces=NS) == "2026-12-31"  # 98006
    ts = dt.datetime.fromisoformat(spec.findtext("crs:Timestamp", namespaces=NS))
    assert now - dt.timedelta(days=365) <= ts <= now + dt.timedelta(days=1)  # 98008
    assert spec.find("crs:CorrMessageRefId", NS) is None  # 80007


def test_body_structure_by_construction():
    root = _root()
    bodies = root.findall("crs:CrsBody", NS)
    assert len(bodies) == 1  # 98100 one CrsBody
    groups = bodies[0].findall("crs:ReportingGroup", NS)
    assert len(groups) == 1  # 60007 one ReportingGroup
    for tag in ("Sponsor", "Intermediary", "PoolReport"):  # 60008, 60009, 60010
        assert groups[0].find(f"crs:{tag}", NS) is None
    fi = bodies[0].find("crs:ReportingFI", NS)
    assert fi.findtext("crs:ResCountryCode", namespaces=NS) == "CH"  # 60013
    doc = fi.find("crs:DocSpec", NS)
    assert doc.findtext("stf:DocTypeIndic", namespaces=NS) == "OECD1"  # 98101 (OECD1/OECD11 only)
    assert doc.find("stf:CorrDocRefId", NS) is None  # 80004
    assert doc.find("stf:CorrMessageRefId", NS) is None  # 80006
    assert doc.findtext("stf:DocRefId", namespaces=NS).startswith("CH2026CH")  # 80001


def test_test_flag_and_file_name_are_consistent():
    prod = _root(test=False)
    test = _root(test=True)
    prod_indics = {e.text for e in prod.iter("{urn:oecd:ties:crsstf:v5}DocTypeIndic")}
    test_indics = {e.text for e in test.iter("{urn:oecd:ties:crsstf:v5}DocTypeIndic")}
    assert prod_indics == {"OECD1"}  # 50010: productive file, no test indicators
    assert test_indics == {"OECD11"}  # 50011: test file, only test indicators
    packaging.check_file_name("Test-x.zip", test=True)  # 50011: name must start with Test
    packaging.check_file_name("x.zip", test=False)  # 50010: productive name must not
