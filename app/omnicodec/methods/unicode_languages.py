"""
Unicode Language & Script Encodings
Japanese (Hiragana, Katakana, Kanji), Chinese, Korean, Arabic, Hebrew, Thai, and more
"""
from __future__ import annotations

import unicodedata
from typing import Any

from ..models import MethodSpec


# =============================================================================
# JAPANESE ENCODINGS
# =============================================================================

# Hiragana Unicode range: U+3040 - U+309F
HIRAGANA_START = 0x3040
# Katakana Unicode range: U+30A0 - U+30FF
KATAKANA_START = 0x30A0
# Hangul (Korean) Unicode range: U+AC00 - U+D7A3
HANGUL_START = 0xAC00
# Arabic Unicode range: U+0600 - U+06FF
ARABIC_START = 0x0600
# Hebrew Unicode range: U+0590 - U+05FF
HEBREW_START = 0x0590
# Thai Unicode range: U+0E00 - U+0E7F
THAI_START = 0x0E00
# Devanagari (Hindi) Unicode range: U+0900 - U+097F
DEVANAGARI_START = 0x0900
# Cyrillic Unicode range: U+0400 - U+04FF
CYRILLIC_START = 0x0400
# Greek Unicode range: U+0370 - U+03FF
GREEK_START = 0x0370


def _to_text(data: bytes, options: dict[str, Any]) -> str:
    return data.decode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


def _to_bytes(text: str, options: dict[str, Any]) -> bytes:
    return text.encode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


# -----------------------------------------------------------------------------
# Hiragana Encoding - Convert ASCII to Hiragana characters
# -----------------------------------------------------------------------------
def hiragana_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert ASCII text to Hiragana-like representation using character mapping."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if 0x20 <= code <= 0x7E:  # Printable ASCII
            # Map to Hiragana range (offset by 0x3040 - 0x20)
            hiragana_code = code + (HIRAGANA_START - 0x20)
            result.append(chr(hiragana_code))
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def hiragana_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert Hiragana back to ASCII."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if HIRAGANA_START <= code < HIRAGANA_START + 0x60:
            # Map back to ASCII
            ascii_code = code - (HIRAGANA_START - 0x20)
            if 0x20 <= ascii_code <= 0x7E:
                result.append(chr(ascii_code))
            else:
                result.append(ch)
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Katakana Encoding - Convert ASCII to Katakana characters
# -----------------------------------------------------------------------------
def katakana_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert ASCII text to Katakana-like representation."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if 0x20 <= code <= 0x7E:
            katakana_code = code + (KATAKANA_START - 0x20)
            result.append(chr(katakana_code))
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def katakana_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert Katakana back to ASCII."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if KATAKANA_START <= code < KATAKANA_START + 0x60:
            ascii_code = code - (KATAKANA_START - 0x20)
            if 0x20 <= ascii_code <= 0x7E:
                result.append(chr(ascii_code))
            else:
                result.append(ch)
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Hangul (Korean) Encoding
# -----------------------------------------------------------------------------
def hangul_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert ASCII bytes to Hangul syllables."""
    result = []
    for byte in data:
        if 0x20 <= byte <= 0x7E:
            # Map to Hangul syllable block
            hangul_code = HANGUL_START + ((byte - 0x20) * 0x100)
            result.append(chr(hangul_code % 0xD7A4))
        else:
            result.append(chr(byte))
    return "".join(result).encode("utf-8")


def hangul_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert Hangul back to ASCII."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            # Reverse mapping (approximate)
            byte = ((code - HANGUL_START) // 0x100) + 0x20
            if 0x20 <= byte <= 0x7E:
                result.append(chr(byte))
            else:
                result.append("?")
        elif code < 128:
            result.append(ch)
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Arabic Encoding
# -----------------------------------------------------------------------------
def arabic_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert ASCII to Arabic script representation."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if 0x20 <= code <= 0x7E:
            arabic_code = code + (ARABIC_START - 0x20)
            result.append(chr(arabic_code))
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def arabic_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert Arabic back to ASCII."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if ARABIC_START <= code < ARABIC_START + 0x60:
            ascii_code = code - (ARABIC_START - 0x20)
            if 0x20 <= ascii_code <= 0x7E:
                result.append(chr(ascii_code))
            else:
                result.append(ch)
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Hebrew Encoding
# -----------------------------------------------------------------------------
def hebrew_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert ASCII to Hebrew script representation."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if 0x20 <= code <= 0x7E:
            hebrew_code = code + (HEBREW_START - 0x20)
            result.append(chr(hebrew_code))
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def hebrew_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert Hebrew back to ASCII."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if HEBREW_START <= code < HEBREW_START + 0x60:
            ascii_code = code - (HEBREW_START - 0x20)
            if 0x20 <= ascii_code <= 0x7E:
                result.append(chr(ascii_code))
            else:
                result.append(ch)
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Thai Encoding
# -----------------------------------------------------------------------------
def thai_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert ASCII to Thai script representation."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if 0x20 <= code <= 0x7E:
            thai_code = code + (THAI_START - 0x20)
            result.append(chr(thai_code))
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def thai_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert Thai back to ASCII."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if THAI_START <= code < THAI_START + 0x60:
            ascii_code = code - (THAI_START - 0x20)
            if 0x20 <= ascii_code <= 0x7E:
                result.append(chr(ascii_code))
            else:
                result.append(ch)
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Devanagari (Hindi) Encoding
# -----------------------------------------------------------------------------
def devanagari_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert ASCII to Devanagari script representation."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if 0x20 <= code <= 0x7E:
            devanagari_code = code + (DEVANAGARI_START - 0x20)
            result.append(chr(devanagari_code))
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def devanagari_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert Devanagari back to ASCII."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if DEVANAGARI_START <= code < DEVANAGARI_START + 0x60:
            ascii_code = code - (DEVANAGARI_START - 0x20)
            if 0x20 <= ascii_code <= 0x7E:
                result.append(chr(ascii_code))
            else:
                result.append(ch)
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Cyrillic (Russian) Encoding
# -----------------------------------------------------------------------------
def cyrillic_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert ASCII to Cyrillic script representation."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if 0x20 <= code <= 0x7E:
            cyrillic_code = code + (CYRILLIC_START - 0x20)
            result.append(chr(cyrillic_code))
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def cyrillic_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert Cyrillic back to ASCII."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if CYRILLIC_START <= code < CYRILLIC_START + 0x60:
            ascii_code = code - (CYRILLIC_START - 0x20)
            if 0x20 <= ascii_code <= 0x7E:
                result.append(chr(ascii_code))
            else:
                result.append(ch)
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Greek Encoding
# -----------------------------------------------------------------------------
def greek_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert ASCII to Greek script representation."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if 0x20 <= code <= 0x7E:
            greek_code = code + (GREEK_START - 0x20)
            result.append(chr(greek_code))
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def greek_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert Greek back to ASCII."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if GREEK_START <= code < GREEK_START + 0x60:
            ascii_code = code - (GREEK_START - 0x20)
            if 0x20 <= ascii_code <= 0x7E:
                result.append(chr(ascii_code))
            else:
                result.append(ch)
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Unicode Normalization Forms
# -----------------------------------------------------------------------------
def nfc_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Normalize to NFC (Canonical Decomposition, Canonical Composition)."""
    text = _to_text(data, options)
    return unicodedata.normalize("NFC", text).encode("utf-8")


def nfd_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Normalize to NFD (Canonical Decomposition)."""
    text = _to_text(data, options)
    return unicodedata.normalize("NFD", text).encode("utf-8")


def nfkc_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Normalize to NFKC (Compatibility Decomposition, Canonical Composition)."""
    text = _to_text(data, options)
    return unicodedata.normalize("NFKC", text).encode("utf-8")


def nfkd_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Normalize to NFKD (Compatibility Decomposition)."""
    text = _to_text(data, options)
    return unicodedata.normalize("NFKD", text).encode("utf-8")


# -----------------------------------------------------------------------------
# Chinese Simplified/Traditional (using character mapping)
# -----------------------------------------------------------------------------
def chinese_simplified_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert traditional Chinese characters to simplified (basic mapping)."""
    text = _to_text(data, options)
    # Basic traditional to simplified mapping (common characters)
    trad_to_simp = {
        "愛": "爱", "寶": "宝", "國": "国", "學": "学", "會": "会",
        "來": "来", "電": "电", "車": "车", "門": "门", "馬": "马",
        "鳥": "鸟", "魚": "鱼", "龍": "龙", "鳳": "凤", "華": "华",
        "語": "语", "文": "文", "體": "体", "製": "制", "為": "为",
    }
    result = "".join(trad_to_simp.get(ch, ch) for ch in text)
    return result.encode("utf-8")


def chinese_traditional_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert simplified Chinese characters to traditional (basic mapping)."""
    text = _to_text(data, options)
    # Basic simplified to traditional mapping (common characters)
    simp_to_trad = {v: k for k, v in {
        "愛": "爱", "寶": "宝", "國": "国", "學": "学", "會": "会",
        "來": "来", "電": "电", "車": "车", "門": "门", "馬": "马",
        "鳥": "鸟", "魚": "鱼", "龍": "龙", "鳳": "凤", "華": "华",
        "語": "语", "文": "文", "體": "体", "製": "制", "為": "为",
    }.items()}
    result = "".join(simp_to_trad.get(ch, ch) for ch in text)
    return result.encode("utf-8")


# Aliases for backward compatibility
chinese_simplified_decode = chinese_traditional_encode
chinese_traditional_decode = chinese_simplified_encode


def get_specs() -> list[MethodSpec]:
    return [
        # Japanese
        MethodSpec("hiragana", "unicode_languages", "ASCII to Hiragana script", hiragana_encode, hiragana_decode, aliases=("hira",)),
        MethodSpec("katakana", "unicode_languages", "ASCII to Katakana script", katakana_encode, katakana_decode, aliases=("kata",)),
        
        # Korean
        MethodSpec("hangul", "unicode_languages", "ASCII to Hangul (Korean)", hangul_encode, hangul_decode, aliases=("korean",)),
        
        # Middle Eastern
        MethodSpec("arabic", "unicode_languages", "ASCII to Arabic script", arabic_encode, arabic_decode),
        MethodSpec("hebrew", "unicode_languages", "ASCII to Hebrew script", hebrew_encode, hebrew_decode),
        
        # Asian
        MethodSpec("thai", "unicode_languages", "ASCII to Thai script", thai_encode, thai_decode),
        MethodSpec("devanagari", "unicode_languages", "ASCII to Devanagari (Hindi)", devanagari_encode, devanagari_decode, aliases=("hindi",)),
        
        # European
        MethodSpec("cyrillic", "unicode_languages", "ASCII to Cyrillic (Russian)", cyrillic_encode, cyrillic_decode, aliases=("russian",)),
        MethodSpec("greek", "unicode_languages", "ASCII to Greek script", greek_encode, greek_decode),
        
        # Chinese
        MethodSpec("chinese_simplified", "unicode_languages", "Traditional to Simplified Chinese", chinese_simplified_encode, chinese_simplified_decode, aliases=("zh_sim",)),
        MethodSpec("chinese_traditional", "unicode_languages", "Simplified to Traditional Chinese", chinese_traditional_encode, chinese_traditional_decode, aliases=("zh_trad",)),
        
        # Unicode Normalization
        MethodSpec("nfc", "unicode_languages", "Unicode NFC normalization", nfc_encode, None),
        MethodSpec("nfd", "unicode_languages", "Unicode NFD normalization", nfd_encode, None),
        MethodSpec("nfkc", "unicode_languages", "Unicode NFKC normalization", nfkc_encode, None),
        MethodSpec("nfkd", "unicode_languages", "Unicode NFKD normalization", nfkd_encode, None),
    ]
