"""Tests for the ESTV transfer package (Wegleitung Ziffer 3.3.1, 4.1.1).

Byte-for-byte comparison with the ESTV Encryptor is impossible (random IV and RSA padding).
These tests cover (a) the round trip with our own key pair and (b) the package structure.
(c), acceptance by the ESTV test channel, needs a registered reporting FI.
"""

import io
import zipfile

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from aeoi.estv import packaging as pk

XML = b'<?xml version="1.0" encoding="UTF-8"?><crs:CRS_OECD version="3.0"/>'


@pytest.fixture(scope="module", params=[2048, 4096])
def key_pair(request):
    private = rsa.generate_private_key(public_exponent=65537, key_size=request.param)
    return private, private.public_key()


def test_round_trip_restores_the_xml(key_pair):
    private, public = key_pair
    package, info = pk.build_package(XML, public, file_name="Test-roundtrip.zip", test=True)
    assert pk.unpackage(package, private) == XML
    assert info.xml_bytes == len(XML)
    assert info.key_blob_bytes == public.key_size // 8
    assert info.package_sha256 == pk.sha256_hex(package)


def test_two_packages_of_the_same_xml_differ(key_pair):
    _, public = key_pair
    a, _ = pk.build_package(XML, public, file_name="Test-a.zip", test=True)
    b, _ = pk.build_package(XML, public, file_name="Test-b.zip", test=True)
    assert a != b  # fresh AES key/IV and random RSA padding every time


def test_structure_matches_wegleitung(key_pair):
    """Also OECD 50013 (AES key size / cipher mode / IV) by construction: CBC, 48-byte blob, IV."""
    private, public = key_pair
    package, _ = pk.build_package(XML, public, file_name="Test-structure.zip", test=True)
    outer = zipfile.ZipFile(io.BytesIO(package))
    assert sorted(outer.namelist()) == ["CRS_KEY", "CRS_Payload"]
    assert len(outer.read("CRS_KEY")) == public.key_size // 8
    assert len(outer.read("CRS_Payload")) % 16 == 0
    # the decrypted payload is a zip with exactly CRS_Payload.xml
    from cryptography.hazmat.primitives.asymmetric import padding as ap

    key_iv = private.decrypt(outer.read("CRS_KEY"), ap.PKCS1v15())
    assert len(key_iv) == 48
    inner_zip = pk.decrypt_payload(outer.read("CRS_Payload"), key_iv[:32], key_iv[32:])
    assert zipfile.ZipFile(io.BytesIO(inner_zip)).namelist() == ["CRS_Payload.xml"]
    result = pk.inspect_package(
        package, public_key=public, file_name="Test-structure.zip", test=True
    )
    assert result.ok, result.problems


def test_inspect_flags_wrong_entries(key_pair):
    _, public = key_pair
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("CRS_Payload", b"\x00" * 15)
        zf.writestr("WRONG", b"x")
    result = pk.inspect_package(buf.getvalue(), public_key=public)
    assert not result.ok
    assert any("exactly CRS_Payload and CRS_KEY" in p for p in result.problems)
    assert any("multiple of 16" in p for p in result.problems)


@pytest.mark.parametrize(
    "name,test,ok",
    [
        ("Testfile123.zip", True, True),
        ("testfile.zip", True, True),  # case-insensitive per Wegleitung
        ("prod.zip", True, False),
        ("prod.zip", False, True),
        ("Test-prod.zip", False, False),
        ("file.xml", False, False),
    ],
)
def test_file_name_rule(name, test, ok):
    if ok:
        pk.check_file_name(name, test=test)
    else:
        with pytest.raises(pk.PackagingError):
            pk.check_file_name(name, test=test)


def test_xml_size_limit(key_pair):
    _, public = key_pair
    too_big = b"x" * (pk.MAX_XML_BYTES + 1)
    with pytest.raises(pk.PackagingError, match="100 MB"):
        pk.build_package(too_big, public, file_name="Test-big.zip", test=True)


def test_package_size_limit(key_pair, monkeypatch):
    _, public = key_pair
    monkeypatch.setattr(pk, "MAX_PACKAGE_BYTES", 1024)
    import os

    incompressible = os.urandom(4096)
    with pytest.raises(pk.PackagingError, match="10 MB"):
        pk.build_package(incompressible, public, file_name="Test-pkg.zip", test=True)


def test_load_public_key_from_pem_and_certificate(key_pair, tmp_path):
    private, public = key_pair
    pem = public.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    assert pk.load_public_key(pem).public_numbers() == public.public_numbers()
    path = tmp_path / "ESTV-PublicKey.pem"
    path.write_bytes(pem)
    assert pk.load_public_key(path).public_numbers() == public.public_numbers()
    assert pk.load_public_key(str(path)).public_numbers() == public.public_numbers()

    import datetime

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    from cryptography.x509.oid import NameOID

    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test")])
    now = datetime.datetime.now(datetime.UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(public)
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=1))
        .sign(private, hashes.SHA256())
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    assert pk.load_public_key(cert_pem).public_numbers() == public.public_numbers()


def test_limits_are_decimal_megabytes():
    assert pk.MAX_XML_BYTES == 100_000_000
    assert pk.MAX_PACKAGE_BYTES == 10_000_000
