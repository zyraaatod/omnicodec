from __future__ import annotations

import binascii
import quopri
import re
import uuid
from typing import Any

from ..models import MethodSpec


_MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....",
    "I": "..", "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.",
    "Q": "--.-", "R": ".-.", "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.", " ": "/",
}
_REV_MORSE = {v: k for k, v in _MORSE.items()}

_DNA_MAP = {"00": "A", "01": "C", "10": "G", "11": "T"}
_REV_DNA = {v: k for k, v in _DNA_MAP.items()}

_LEET_MAP = str.maketrans({"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7", "A": "4", "E": "3", "I": "1", "O": "0", "S": "5", "T": "7"})
_LEET_REV = str.maketrans({"4": "a", "3": "e", "1": "i", "0": "o", "5": "s", "7": "t"})


def morse_encode(data: bytes, options: dict[str, Any]) -> bytes:
    text = data.decode("utf-8", errors="replace").upper()
    return " ".join(_MORSE.get(ch, "?") for ch in text).encode("ascii")


def morse_decode(data: bytes, options: dict[str, Any]) -> bytes:
    parts = data.decode("ascii", errors="ignore").split()
    return "".join(_REV_MORSE.get(p, "?") for p in parts).encode("utf-8")


def dna_encode(data: bytes, options: dict[str, Any]) -> bytes:
    bits = "".join(f"{b:08b}" for b in data)
    return "".join(_DNA_MAP[bits[i : i + 2]] for i in range(0, len(bits), 2)).encode("ascii")


def dna_decode(data: bytes, options: dict[str, Any]) -> bytes:
    text = re.sub(r"\s+", "", data.decode("ascii", errors="ignore").upper())
    bits = "".join(_REV_DNA[ch] for ch in text)
    if len(bits) % 8 != 0:
        raise ValueError("DNA stream invalid length")
    return bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))


def leet_encode(data: bytes, options: dict[str, Any]) -> bytes:
    return data.decode("utf-8", errors="replace").translate(_LEET_MAP).encode("utf-8")


def leet_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return data.decode("utf-8", errors="replace").translate(_LEET_REV).encode("utf-8")


def quoted_printable_encode(data: bytes, options: dict[str, Any]) -> bytes:
    return quopri.encodestring(data, quotetabs=True)


def quoted_printable_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return quopri.decodestring(data)


def uuencode_encode(data: bytes, options: dict[str, Any]) -> bytes:
    line = binascii.b2a_uu(data)
    return line.rstrip(b"\n")


def uuencode_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return binascii.a2b_uu(data + (b"\n" if not data.endswith(b"\n") else b""))


def uuid5_encode(data: bytes, options: dict[str, Any]) -> bytes:
    namespace = options.get("namespace", "dns")
    ns_map = {
        "dns": uuid.NAMESPACE_DNS,
        "url": uuid.NAMESPACE_URL,
        "oid": uuid.NAMESPACE_OID,
        "x500": uuid.NAMESPACE_X500,
    }
    ns = ns_map.get(namespace, uuid.NAMESPACE_DNS)
    return str(uuid.uuid5(ns, data.decode("utf-8", errors="replace"))).encode("ascii")


def uuid_parse_decode(data: bytes, options: dict[str, Any]) -> bytes:
    u = uuid.UUID(data.decode("ascii").strip())
    return u.bytes


def uuid_bytes_encode(data: bytes, options: dict[str, Any]) -> bytes:
    if len(data) != 16:
        raise ValueError("UUID bytes encode expects exactly 16 bytes")
    return str(uuid.UUID(bytes=data)).encode("ascii")


def get_specs() -> list[MethodSpec]:
    return [
        MethodSpec("morse", "visual_signal", "Morse code", morse_encode, morse_decode),
        MethodSpec("dna", "domain_esoteric", "DNA nucleotide codec", dna_encode, dna_decode),
        MethodSpec("leet", "unicode_style", "Leetspeak transform", leet_encode, leet_decode),
        MethodSpec("quoted_printable", "mail_legacy", "Quoted-printable MIME", quoted_printable_encode, quoted_printable_decode, aliases=("qp",)),
        MethodSpec("uuencode", "mail_legacy", "UUEncode single-line block", uuencode_encode, uuencode_decode, aliases=("uu",)),
        MethodSpec("uuid_parse", "domain_esoteric", "UUID string to 16-byte payload", uuid_bytes_encode, uuid_parse_decode),
    ]
