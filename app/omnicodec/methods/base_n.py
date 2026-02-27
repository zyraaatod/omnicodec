from __future__ import annotations

import base64
import binascii
from typing import Any

from ..models import MethodSpec


_BASE58_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_BASE62_ALPHABET = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def _wrap_ascii(text: str, width: int) -> str:
    if width <= 0:
        return text
    return "\n".join(text[i : i + width] for i in range(0, len(text), width))


def _baseX_encode(data: bytes, alphabet: bytes) -> bytes:
    if not data:
        return b""
    value = int.from_bytes(data, "big")
    base = len(alphabet)
    encoded = bytearray()
    while value > 0:
        value, rem = divmod(value, base)
        encoded.insert(0, alphabet[rem])
    leading_zeros = len(data) - len(data.lstrip(b"\x00"))
    return bytes(alphabet[0:1] * leading_zeros + encoded)


def _baseX_decode(data: bytes, alphabet: bytes) -> bytes:
    s = data.strip()
    if not s:
        return b""
    base = len(alphabet)
    index = {c: i for i, c in enumerate(alphabet)}
    value = 0
    for ch in s:
        if ch not in index:
            raise ValueError("Invalid character for base alphabet")
        value = value * base + index[ch]
    decoded = value.to_bytes((value.bit_length() + 7) // 8, "big") if value > 0 else b""
    leading = 0
    for ch in s:
        if ch == alphabet[0]:
            leading += 1
        else:
            break
    return b"\x00" * leading + decoded


def base64_encode(data: bytes, options: dict[str, Any]) -> bytes:
    raw = base64.b64encode(data).decode("ascii")
    width = int(options.get("wrap", 76))
    return _wrap_ascii(raw, width).encode("ascii")


def base64_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return base64.b64decode(data.replace(b"\n", b""), validate=bool(options.get("validate", True)))


def base64url_encode(data: bytes, options: dict[str, Any]) -> bytes:
    raw = base64.urlsafe_b64encode(data).decode("ascii")
    if options.get("strip_padding", False):
        raw = raw.rstrip("=")
    return raw.encode("ascii")


def base64url_decode(data: bytes, options: dict[str, Any]) -> bytes:
    s = data.decode("ascii").strip()
    pad = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode((s + pad).encode("ascii"))


def base32_encode(data: bytes, options: dict[str, Any]) -> bytes:
    return base64.b32encode(data)


def base32_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return base64.b32decode(data, casefold=True)


def base32hex_encode(data: bytes, options: dict[str, Any]) -> bytes:
    return base64.b32hexencode(data)


def base32hex_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return base64.b32hexdecode(data, casefold=True)


def base16_encode(data: bytes, options: dict[str, Any]) -> bytes:
    upper = bool(options.get("upper", False))
    out = base64.b16encode(data)
    return out if upper else out.lower()


def base16_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return base64.b16decode(data.upper())


def base85_encode(data: bytes, options: dict[str, Any]) -> bytes:
    variant = options.get("variant", "ascii85")
    if variant == "z85":
        return base64.b85encode(data)
    return base64.a85encode(data)


def base85_decode(data: bytes, options: dict[str, Any]) -> bytes:
    variant = options.get("variant", "ascii85")
    if variant == "z85":
        return base64.b85decode(data)
    return base64.a85decode(data)


def base58_encode(data: bytes, options: dict[str, Any]) -> bytes:
    return _baseX_encode(data, _BASE58_ALPHABET)


def base58_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return _baseX_decode(data, _BASE58_ALPHABET)


def base62_encode(data: bytes, options: dict[str, Any]) -> bytes:
    return _baseX_encode(data, _BASE62_ALPHABET)


def base62_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return _baseX_decode(data, _BASE62_ALPHABET)


def hex_encode(data: bytes, options: dict[str, Any]) -> bytes:
    out = binascii.hexlify(data).decode("ascii")
    if options.get("upper", False):
        out = out.upper()
    if options.get("byte_spacing", False):
        out = " ".join(out[i : i + 2] for i in range(0, len(out), 2))
    return out.encode("ascii")


def hex_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return binascii.unhexlify(data.replace(b" ", b""))


def binary_encode(data: bytes, options: dict[str, Any]) -> bytes:
    sep = options.get("sep", "")
    bits = [format(b, "08b") for b in data]
    return sep.join(bits).encode("ascii")


def binary_decode(data: bytes, options: dict[str, Any]) -> bytes:
    bitstr = data.decode("ascii").replace(" ", "").replace("\n", "")
    if len(bitstr) % 8:
        raise ValueError("Binary data length must be multiple of 8")
    return bytes(int(bitstr[i : i + 8], 2) for i in range(0, len(bitstr), 8))


def octal_encode(data: bytes, options: dict[str, Any]) -> bytes:
    sep = options.get("sep", " ")
    return sep.join(format(b, "03o") for b in data).encode("ascii")


def octal_decode(data: bytes, options: dict[str, Any]) -> bytes:
    text = data.decode("ascii").strip()
    parts = text.split() if " " in text else [text[i : i + 3] for i in range(0, len(text), 3)]
    return bytes(int(x, 8) for x in parts if x)


def get_specs() -> list[MethodSpec]:
    return [
        MethodSpec("base64", "base_n", "RFC 4648 Base64", base64_encode, base64_decode, aliases=("b64",), extensions=(".b64",)),
        MethodSpec("base64url", "base_n", "URL-safe Base64", base64url_encode, base64url_decode, aliases=("b64url",)),
        MethodSpec("base32", "base_n", "RFC 4648 Base32", base32_encode, base32_decode),
        MethodSpec("base16", "base_n", "Base16 encoding", base16_encode, base16_decode, aliases=("hex16",)),
        MethodSpec("base85", "base_n", "Ascii85 / Z85 style", base85_encode, base85_decode, aliases=("ascii85", "b85")),
        MethodSpec("base58", "base_n", "Bitcoin Base58 alphabet", base58_encode, base58_decode),
        MethodSpec("base62", "base_n", "Alphanumeric Base62", base62_encode, base62_decode),
        MethodSpec("hex", "binary_text", "Hexadecimal representation", hex_encode, hex_decode),
        MethodSpec("binary", "binary_text", "Binary bitstring", binary_encode, binary_decode, aliases=("bin",)),
        MethodSpec("octal", "binary_text", "Octal byte representation", octal_encode, octal_decode, aliases=("oct",)),
    ]
