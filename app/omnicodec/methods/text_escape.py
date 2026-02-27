from __future__ import annotations

import html
import json
import urllib.parse
from typing import Any

from ..models import MethodSpec


_FULLWIDTH_OFFSET = 0xFEE0


def _to_text(data: bytes, options: dict[str, Any]) -> str:
    return data.decode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


def _to_bytes(text: str, options: dict[str, Any]) -> bytes:
    return text.encode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


def url_encode(data: bytes, options: dict[str, Any]) -> bytes:
    text = _to_text(data, options)
    safe = options.get("safe", "")
    return urllib.parse.quote(text, safe=safe).encode("ascii")


def url_decode(data: bytes, options: dict[str, Any]) -> bytes:
    text = _to_text(data, options)
    return urllib.parse.unquote(text).encode("utf-8")


def html_entity_encode(data: bytes, options: dict[str, Any]) -> bytes:
    text = _to_text(data, options)
    return html.escape(text, quote=True).encode("utf-8")


def html_entity_decode(data: bytes, options: dict[str, Any]) -> bytes:
    text = _to_text(data, options)
    return html.unescape(text).encode("utf-8")


def json_escape_encode(data: bytes, options: dict[str, Any]) -> bytes:
    text = _to_text(data, options)
    payload = json.dumps(text, ensure_ascii=bool(options.get("ensure_ascii", False)))
    return payload[1:-1].encode("utf-8")


def json_escape_decode(data: bytes, options: dict[str, Any]) -> bytes:
    text = _to_text(data, options)
    return json.loads(f'"{text}"').encode("utf-8")


def unicode_escape_encode(data: bytes, options: dict[str, Any]) -> bytes:
    text = _to_text(data, options)
    style = options.get("style", "u")
    out: list[str] = []
    for ch in text:
        code = ord(ch)
        if style == "x" and code <= 0xFF:
            out.append(f"\\x{code:02x}")
        elif style == "U":
            out.append(f"\\U{code:08x}")
        else:
            out.append(f"\\u{code:04x}")
    return "".join(out).encode("ascii")


def unicode_escape_decode(data: bytes, options: dict[str, Any]) -> bytes:
    text = data.decode("ascii")
    decoded = text.encode("ascii").decode("unicode_escape")
    return decoded.encode("utf-8")


def fullwidth_encode(data: bytes, options: dict[str, Any]) -> bytes:
    text = _to_text(data, options)
    out = []
    for ch in text:
        if ch == " ":
            out.append("\u3000")
        elif 33 <= ord(ch) <= 126:
            out.append(chr(ord(ch) + _FULLWIDTH_OFFSET))
        else:
            out.append(ch)
    return "".join(out).encode("utf-8")


def fullwidth_decode(data: bytes, options: dict[str, Any]) -> bytes:
    text = _to_text(data, options)
    out = []
    for ch in text:
        code = ord(ch)
        if ch == "\u3000":
            out.append(" ")
        elif 0xFF01 <= code <= 0xFF5E:
            out.append(chr(code - _FULLWIDTH_OFFSET))
        else:
            out.append(ch)
    return "".join(out).encode("utf-8")


def rot13_encode(data: bytes, options: dict[str, Any]) -> bytes:
    text = _to_text(data, options)
    return text.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm",
    )).encode("utf-8")


def rot13_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return rot13_encode(data, options)


def punycode_encode(data: bytes, options: dict[str, Any]) -> bytes:
    text = _to_text(data, options)
    return text.encode("punycode")


def punycode_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return data.decode("ascii").encode("ascii").decode("punycode").encode("utf-8")


def get_specs() -> list[MethodSpec]:
    return [
        MethodSpec("url", "web_escape", "URL percent encoding", url_encode, url_decode, aliases=("urlencode", "percent")),
        MethodSpec("html_entity", "web_escape", "HTML entities", html_entity_encode, html_entity_decode, aliases=("html",)),
        MethodSpec("json_escape", "web_escape", "JSON string escaping", json_escape_encode, json_escape_decode),
        MethodSpec("unicode_escape", "web_escape", "Unicode escape sequences", unicode_escape_encode, unicode_escape_decode, aliases=("uescape",)),
        MethodSpec("fullwidth", "unicode_style", "ASCII to fullwidth conversion", fullwidth_encode, fullwidth_decode),
        MethodSpec("rot13", "unicode_style", "ROT13 Caesar transform", rot13_encode, rot13_decode),
        MethodSpec("punycode", "web_escape", "IDNA punycode transform", punycode_encode, punycode_decode),
    ]
