"""Packaging and encryption of CRS XML files for the ESTV AIA portal.

Implements Technische Wegleitung AIA (ESTV, 09.2026), Ziffer 3.3.1 "Verschluesselung mittels
eigenem Tool":

1. The CRS XML file must be named ``CRS_Payload.xml`` and zipped -> ``CRS_Payload.zip``.
2. ``CRS_Payload.zip`` is encrypted with AES-256, CBC mode, 16-byte IV (new for every
   encryption), 32-byte key, PKCS#7 padding, no encoding -> file ``CRS_Payload``.
3. Key (32 bytes) + IV (16 bytes) are concatenated (48 bytes) and encrypted with RSA,
   PKCS#1 v1.5 padding, using the public key of the ESTV AIA certificate -> file ``CRS_KEY``.
4. A zip with exactly ``CRS_Payload`` and ``CRS_KEY`` is the transfer package. Any file name
   with extension ``.zip``; for test messages the name must start with ``Test``
   (case-insensitive).

Limits (Ziffer 4.1.1): XML at most 100 MB; the compressed/encrypted upload at most 10 MB.
The XML must NOT be signed (Ziffer 5.2, error 50007).

Because the AES key/IV and the RSA padding are random, two packages of the same XML never
match byte for byte. The correct tests are (a) a round trip with a test key pair, (b) the
structural checks in :func:`inspect_package`, (c) the acceptance by the ESTV test channel.
"""

from __future__ import annotations

import io
import os
import zipfile
from dataclasses import dataclass
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PAYLOAD_XML_NAME = "CRS_Payload.xml"
PAYLOAD_ENTRY = "CRS_Payload"
KEY_ENTRY = "CRS_KEY"
AES_KEY_BYTES = 32
AES_IV_BYTES = 16
KEY_BLOB_BYTES = AES_KEY_BYTES + AES_IV_BYTES  # 48
# Ziffer 4.1.1 says "100 MB" / "10 MB" without defining the unit; the decimal reading is the
# stricter one, so a file we accept is never one the portal rejects for size.
MAX_XML_BYTES = 100_000_000
MAX_PACKAGE_BYTES = 10_000_000
TEST_PREFIX = "test"


class PackagingError(ValueError):
    """A package could not be built or does not follow the ESTV structure."""


def load_public_key(pem: bytes | str | Path) -> rsa.RSAPublicKey:
    """Load the ESTV public key from a certificate or a public key, PEM or DER (.cer/.crt/.der).

    The ESTV distributes ``ESTV-PublicKey.pem`` inside the Encryptor archive and the AIA
    certificate on the XML upload page of the AIA application (Ziffer 3.3); the portal may hand
    out either encoding. A ``str`` without a PEM header is treated as a file path.
    """
    if isinstance(pem, Path):
        data = pem.read_bytes()
    elif isinstance(pem, str) and "-----BEGIN" not in pem:
        data = Path(pem).read_bytes()
    else:
        data = pem.encode() if isinstance(pem, str) else bytes(pem)
    loaders = (
        lambda d: x509.load_pem_x509_certificate(d).public_key(),
        serialization.load_pem_public_key,
        lambda d: x509.load_der_x509_certificate(d).public_key(),
        serialization.load_der_public_key,
    )
    key = None
    for load in loaders:
        try:
            key = load(data)
            break
        except (ValueError, TypeError):
            continue
    if key is None:
        raise PackagingError(
            "not a public key or certificate (expected PEM or DER: .pem, .cer, .crt, .der)"
        )
    if not isinstance(key, rsa.RSAPublicKey):
        raise PackagingError("The ESTV key must be an RSA public key")
    return key


def public_key_pem(key: rsa.RSAPublicKey) -> str:
    """The key as PEM text (SubjectPublicKeyInfo) - the form the registry stores."""
    return key.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("ascii")


@dataclass(frozen=True)
class PackageInfo:
    xml_bytes: int
    inner_zip_bytes: int
    encrypted_payload_bytes: int
    key_blob_bytes: int
    package_bytes: int
    is_test: bool
    file_name: str
    package_sha256: str


def check_file_name(file_name: str, *, test: bool) -> None:
    """Ziffer 3.3.1 / 5.3.5: test packages start with 'Test'; productive packages must not."""
    name = Path(file_name).name
    if not name.lower().endswith(".zip"):
        raise PackagingError(f"Package file name must end with .zip: {name!r}")
    starts_with_test = name.lower().startswith(TEST_PREFIX)
    if test and not starts_with_test:
        raise PackagingError(f"Test packages must be named 'Test*.zip' (got {name!r})")
    if not test and starts_with_test:
        raise PackagingError(f"Productive packages must not start with 'Test' (got {name!r})")


def _zip_single(name: str, data: bytes) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(name, data)
    return buf.getvalue()


def encrypt_payload(inner_zip: bytes, key: bytes, iv: bytes) -> bytes:
    """AES-256-CBC with PKCS#7 padding (Ziffer 3.3.1, step 2)."""
    padder = padding.PKCS7(128).padder()
    padded = padder.update(inner_zip) + padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return encryptor.update(padded) + encryptor.finalize()


def decrypt_payload(encrypted: bytes, key: bytes, iv: bytes) -> bytes:
    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    padded = decryptor.update(encrypted) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()


def sha256_hex(data: bytes) -> str:
    """SHA-256 of the uploaded file; the portal shows it next to each upload (Ziffer 3.4)."""
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data)
    return digest.finalize().hex()


def build_package(
    xml: bytes,
    public_key: rsa.RSAPublicKey,
    *,
    file_name: str,
    test: bool,
) -> tuple[bytes, PackageInfo]:
    """Build the ESTV transfer package for one CRS XML document.

    Returns the zip bytes and a :class:`PackageInfo`. Raises :class:`PackagingError` when the
    XML exceeds 100 MB, the package exceeds 10 MB, or the file name breaks the Test rule.
    """
    check_file_name(file_name, test=test)
    if len(xml) > MAX_XML_BYTES:
        raise PackagingError(
            f"XML is {len(xml)} bytes, above the 100 MB limit (Ziffer 4.1.1); split the message"
        )
    inner_zip = _zip_single(PAYLOAD_XML_NAME, xml)
    key = os.urandom(AES_KEY_BYTES)
    iv = os.urandom(AES_IV_BYTES)  # new IV for every encryption (Ziffer 3.3.1, Hinweis)
    encrypted = encrypt_payload(inner_zip, key, iv)
    key_blob = public_key.encrypt(key + iv, asym_padding.PKCS1v15())

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(PAYLOAD_ENTRY, encrypted)
        zf.writestr(KEY_ENTRY, key_blob)
    package = buf.getvalue()
    if len(package) > MAX_PACKAGE_BYTES:
        raise PackagingError(
            f"Package is {len(package)} bytes, above the 10 MB limit (Ziffer 4.1.1); "
            "split the message"
        )
    info = PackageInfo(
        xml_bytes=len(xml),
        inner_zip_bytes=len(inner_zip),
        encrypted_payload_bytes=len(encrypted),
        key_blob_bytes=len(key_blob),
        package_bytes=len(package),
        is_test=test,
        file_name=Path(file_name).name,
        package_sha256=sha256_hex(package),
    )
    return package, info


def write_package(
    xml: bytes, public_key: rsa.RSAPublicKey, out_path: str | Path, *, test: bool
) -> PackageInfo:
    out_path = Path(out_path)
    package, info = build_package(xml, public_key, file_name=out_path.name, test=test)
    out_path.write_bytes(package)
    return info


@dataclass(frozen=True)
class InspectionResult:
    ok: bool
    problems: tuple[str, ...]
    entries: tuple[str, ...]
    encrypted_payload_bytes: int | None
    key_blob_bytes: int | None


def inspect_package(
    package: bytes,
    *,
    public_key: rsa.RSAPublicKey | None = None,
    file_name: str | None = None,
    test: bool | None = None,
) -> InspectionResult:
    """Structural check of a transfer package without decrypting it.

    Checks: exactly two entries named CRS_Payload and CRS_KEY; the key blob has the RSA
    modulus size (when a public key is given); the encrypted payload is a non-empty multiple
    of the AES block size; the package is within 10 MB; the file name follows the Test rule.
    """
    problems: list[str] = []
    try:
        zf = zipfile.ZipFile(io.BytesIO(package))
    except zipfile.BadZipFile:
        return InspectionResult(False, ("outer file is not a zip",), (), None, None)
    names = tuple(zf.namelist())
    if sorted(names) != sorted([PAYLOAD_ENTRY, KEY_ENTRY]):
        problems.append(
            f"outer zip must contain exactly {PAYLOAD_ENTRY} and {KEY_ENTRY}, got {names}"
        )
    enc = zf.read(PAYLOAD_ENTRY) if PAYLOAD_ENTRY in names else None
    blob = zf.read(KEY_ENTRY) if KEY_ENTRY in names else None
    if enc is not None and (len(enc) == 0 or len(enc) % 16 != 0):
        problems.append(
            f"{PAYLOAD_ENTRY} length {len(enc)} is not a non-empty multiple of 16 (AES-CBC)"
        )
    if blob is not None and public_key is not None:
        expected = public_key.key_size // 8
        if len(blob) != expected:
            problems.append(
                f"{KEY_ENTRY} is {len(blob)} bytes, expected RSA modulus size {expected}"
            )
    if len(package) > MAX_PACKAGE_BYTES:
        problems.append(f"package is {len(package)} bytes, above the 10 MB limit")
    if file_name is not None and test is not None:
        try:
            check_file_name(file_name, test=test)
        except PackagingError as exc:
            problems.append(str(exc))
    return InspectionResult(
        ok=not problems,
        problems=tuple(problems),
        entries=names,
        encrypted_payload_bytes=len(enc) if enc is not None else None,
        key_blob_bytes=len(blob) if blob is not None else None,
    )


def unpackage(package: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    """Reverse of :func:`build_package`; only possible with the private key (tests use their own pair)."""
    zf = zipfile.ZipFile(io.BytesIO(package))
    blob = zf.read(KEY_ENTRY)
    key_iv = private_key.decrypt(blob, asym_padding.PKCS1v15())
    if len(key_iv) != KEY_BLOB_BYTES:
        raise PackagingError(
            f"decrypted key blob is {len(key_iv)} bytes, expected {KEY_BLOB_BYTES}"
        )
    key, iv = key_iv[:AES_KEY_BYTES], key_iv[AES_KEY_BYTES:]
    inner_zip = decrypt_payload(zf.read(PAYLOAD_ENTRY), key, iv)
    inner = zipfile.ZipFile(io.BytesIO(inner_zip))
    if inner.namelist() != [PAYLOAD_XML_NAME]:
        raise PackagingError(
            f"inner zip must contain exactly {PAYLOAD_XML_NAME}, got {inner.namelist()}"
        )
    return inner.read(PAYLOAD_XML_NAME)
