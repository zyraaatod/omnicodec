from __future__ import annotations

import binascii
import hashlib
import hmac
from typing import Any

from ..models import MethodSpec


def _digest(algo: str):
    def enc(data: bytes, options: dict[str, Any]) -> bytes:
        return hashlib.new(algo, data).hexdigest().encode("ascii")

    def verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
        actual = hashlib.new(algo, data).hexdigest().encode("ascii")
        return hmac.compare_digest(actual.strip().lower(), expected.strip().lower())

    return enc, verify


def hmac_sha256_encode(data: bytes, options: dict[str, Any]) -> bytes:
    key = options.get("key", "")
    if isinstance(key, str):
        key = key.encode("utf-8")
    return hmac.new(key, data, hashlib.sha256).hexdigest().encode("ascii")


def hmac_sha256_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    return hmac.compare_digest(hmac_sha256_encode(data, options).lower(), expected.strip().lower())


def pbkdf2_sha256_encode(data: bytes, options: dict[str, Any]) -> bytes:
    salt = str(options.get("salt", "omnicodec")).encode("utf-8")
    rounds = int(options.get("rounds", 200000))
    dklen = int(options.get("dklen", 32))
    derived = hashlib.pbkdf2_hmac("sha256", data, salt, rounds, dklen=dklen)
    return binascii.hexlify(derived)


def pbkdf2_sha256_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    return hmac.compare_digest(pbkdf2_sha256_encode(data, options).lower(), expected.strip().lower())


def crc32_encode(data: bytes, options: dict[str, Any]) -> bytes:
    return f"{binascii.crc32(data) & 0xFFFFFFFF:08x}".encode("ascii")


def crc32_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    return hmac.compare_digest(crc32_encode(data, options).lower(), expected.strip().lower())


def adler32_encode(data: bytes, options: dict[str, Any]) -> bytes:
    import zlib

    return f"{zlib.adler32(data) & 0xFFFFFFFF:08x}".encode("ascii")


def adler32_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    return hmac.compare_digest(adler32_encode(data, options).lower(), expected.strip().lower())


def get_specs() -> list[MethodSpec]:
    methods: list[MethodSpec] = []
    for algo in ["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sha3_256", "sha3_512", "blake2b", "blake2s"]:
        enc, verify = _digest(algo)
        methods.append(MethodSpec(algo, "crypto_hash", f"{algo} digest", encode=enc, verify=verify))

    methods.extend(
        [
            MethodSpec("hmac_sha256", "crypto_hash", "HMAC-SHA256 digest", encode=hmac_sha256_encode, verify=hmac_sha256_verify),
            MethodSpec("pbkdf2_sha256", "kdf", "PBKDF2-HMAC-SHA256 derive", encode=pbkdf2_sha256_encode, verify=pbkdf2_sha256_verify),
            MethodSpec("crc32", "checksum", "CRC-32 checksum", encode=crc32_encode, verify=crc32_verify),
            MethodSpec("adler32", "checksum", "Adler-32 checksum", encode=adler32_encode, verify=adler32_verify),
        ]
    )
    return methods
