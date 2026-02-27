"""
Auto-detection module for encoded data.
Detects likely encoding methods based on pattern matching and validation.
"""
from __future__ import annotations

import base64
import binascii
import re
from typing import List, Tuple


def _is_printable_utf8(data: bytes) -> bool:
    """Check if data is printable UTF-8 text."""
    try:
        text = data.decode("utf-8")
        return all(c.isprintable() or c.isspace() for c in text)
    except UnicodeDecodeError:
        return False


def _validate_base64(text: str) -> bool:
    """Validate Base64 encoding."""
    try:
        # Remove whitespace
        cleaned = re.sub(r'\s+', '', text)
        # Check padding
        if len(cleaned) % 4 != 0:
            return False
        base64.b64decode(cleaned, validate=True)
        return True
    except (binascii.Error, ValueError):
        return False


def _validate_base64url(text: str) -> bool:
    """Validate Base64URL encoding."""
    try:
        cleaned = re.sub(r'\s+', '', text)
        # Add padding if needed
        pad = '=' * ((4 - len(cleaned) % 4) % 4)
        base64.urlsafe_b64decode(cleaned + pad)
        return True
    except (binascii.Error, ValueError):
        return False


def _validate_hex(text: str) -> bool:
    """Validate hexadecimal encoding."""
    cleaned = re.sub(r'\s+', '', text)
    if len(cleaned) % 2 != 0:
        return False
    try:
        binascii.unhexlify(cleaned)
        return True
    except (binascii.Error, ValueError):
        return False


def _validate_binary(text: str) -> bool:
    """Validate binary string encoding."""
    cleaned = re.sub(r'\s+', '', text)
    if len(cleaned) % 8 != 0:
        return False
    return all(c in '01' for c in cleaned)


def _validate_base32(text: str) -> bool:
    """Validate Base32 encoding."""
    try:
        cleaned = re.sub(r'\s+', '', text).upper()
        # Add padding
        pad = '=' * ((8 - len(cleaned) % 8) % 8)
        base64.b32decode(cleaned + pad)
        return True
    except (binascii.Error, ValueError):
        return False


def _validate_base85(text: str) -> bool:
    """Validate Base85/Ascii85 encoding."""
    try:
        cleaned = re.sub(r'\s+', '', text)
        base64.b85decode(cleaned)
        return True
    except (binascii.Error, ValueError):
        return False


def _validate_url(text: str) -> bool:
    """Validate URL percent encoding."""
    # Check for percent-encoded sequences
    if '%' in text:
        try:
            # Validate hex after %
            matches = re.findall(r'%([0-9A-Fa-f]{2})', text)
            return all(len(m) == 2 for m in matches)
        except Exception:
            return False
    return True


def _validate_html_entity(text: str) -> bool:
    """Validate HTML entity encoding."""
    return bool(re.search(r'&[a-zA-Z]+;|&#\d+;|&#x[0-9A-Fa-f]+;', text))


def _validate_json(text: str) -> bool:
    """Validate JSON encoding."""
    try:
        import json
        json.loads(text)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def _validate_xml(text: str) -> bool:
    """Validate XML encoding."""
    return text.strip().startswith('<') and text.strip().endswith('>')


def _validate_yaml(text: str) -> bool:
    """Validate YAML encoding."""
    # Simple heuristic: contains key: value pattern
    return bool(re.search(r'^[a-zA-Z_]+:\s*', text, re.MULTILINE))


def _validate_morse(text: str) -> bool:
    """Validate Morse code."""
    morse_chars = set('.-/ ')
    cleaned = text.strip().lower()
    return all(c in morse_chars for c in cleaned) and len(cleaned) > 0


def _validate_braille(text: str) -> bool:
    """Validate Braille Unicode."""
    # Braille Unicode range: U+2800 to U+28FF
    return any('\u2800' <= c <= '\u28FF' for c in text)


def _validate_rot13(text: str) -> bool:
    """Validate ROT13 (always valid for ASCII text)."""
    return all(32 <= ord(c) <= 126 for c in text)


def _validate_fullwidth(text: str) -> bool:
    """Validate Fullwidth Unicode."""
    # Fullwidth range: U+FF00 to U+FFEF
    return any('\uFF00' <= c <= '\uFFEF' for c in text)


def _validate_leet(text: str) -> bool:
    """Validate Leetspeak."""
    leet_chars = set('431057@!$')
    return any(c in leet_chars for c in text.lower())


def _validate_unicode_escape(text: str) -> bool:
    """Validate Unicode escape sequences."""
    return bool(re.search(r'\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8}|\\x[0-9A-Fa-f]{2}', text))


def _validate_jwt(text: str) -> bool:
    """Validate JWT format."""
    parts = text.split('.')
    if len(parts) != 3:
        return False
    # Each part should be base64url
    for part in parts:
        try:
            pad = '=' * ((4 - len(part) % 4) % 4)
            base64.urlsafe_b64decode(part + pad)
        except (binascii.Error, ValueError):
            return False
    return True


def _validate_uuid(text: str) -> bool:
    """Validate UUID format."""
    uuid_pattern = r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$'
    return bool(re.match(uuid_pattern, text.strip()))


def _validate_ulid(text: str) -> bool:
    """Validate ULID format."""
    # ULID: 26 characters, base32
    ulid_pattern = r'^[0-9A-HJKMNP-TV-Z]{26}$'
    return bool(re.match(ulid_pattern, text.strip(), re.IGNORECASE))


def _validate_geohash(text: str) -> bool:
    """Validate Geohash format."""
    geohash_chars = set('0123456789bcdefghjkmnpqrstuvwxyz')
    cleaned = text.strip().lower()
    return len(cleaned) >= 4 and all(c in geohash_chars for c in cleaned)


def _validate_mimetype(text: str) -> bool:
    """Validate MIME type format."""
    return bool(re.match(r'^[a-zA-Z0-9]+/[a-zA-Z0-9+\-.]+$', text.strip()))


def _validate_armor(text: str) -> bool:
    """Validate PGP-style armor."""
    return '-----BEGIN' in text and '-----END' in text


def _validate_data_uri(text: str) -> bool:
    """Validate Data URI format."""
    return text.strip().startswith('data:')


def _validate_tar(text: bytes) -> bool:
    """Validate TAR archive."""
    if len(text) < 512:
        return False
    # Check ustar magic at offset 257
    return text[257:263] == b'ustar\x00'


def _validate_compressed(data: bytes) -> bool:
    """Check if data looks like compressed format."""
    # Gzip magic
    if data[:2] == b'\x1f\x8b':
        return True
    # Zlib
    if data[:2] == b'\x78\x9c' or data[:2] == b'\x78\x01' or data[:2] == b'\x78\xda':
        return True
    # Bzip2
    if data[:3] == b'BZh':
        return True
    # XZ
    if data[:6] == b'\xfd7zXZ\x00':
        return True
    return False


def detect_candidates(data: bytes) -> List[str]:
    """
    Detect likely encoding methods for the given data.
    Returns a list of method keys that could decode this data.
    """
    if not data:
        return []
    
    text = data.decode("utf-8", errors="ignore").strip()
    out: List[Tuple[str, int]] = []  # (method, confidence score)
    
    if not text:
        # Binary data - check for compression
        if _validate_compressed(data):
            if data[:2] == b'\x1f\x8b':
                out.append(("gzip", 100))
            elif data[:2] in (b'\x78\x9c', b'\x78\x01', b'\x78\xda'):
                out.append(("zlib", 100))
            elif data[:3] == b'BZh':
                out.append(("bzip2", 100))
            elif data[:6] == b'\xfd7zXZ\x00':
                out.append(("xz", 100))
        # Check for TAR
        if _validate_tar(data):
            out.append(("tar", 100))
        return [m[0] for m in out]
    
    # Text-based detection
    # Base64
    if re.fullmatch(r'[A-Za-z0-9+/=\s]{4,}', text):
        if _validate_base64(text):
            out.append(("base64", 95))
    
    # Base64URL
    if re.fullmatch(r'[A-Za-z0-9\-_=\s]{4,}', text):
        if _validate_base64url(text):
            out.append(("base64url", 90))
    
    # Hex
    if re.fullmatch(r'[A-Fa-f0-9\s]+', text) and len(text.replace(" ", "")) % 2 == 0:
        if _validate_hex(text):
            out.append(("hex", 95))
    
    # Binary
    if re.fullmatch(r'[01\s]+', text):
        if _validate_binary(text):
            out.append(("binary", 95))
    
    # Base32
    if re.fullmatch(r'[A-Z2-7=]+\s*', text, re.IGNORECASE):
        if _validate_base32(text):
            out.append(("base32", 90))
    
    # Base85/Ascii85
    if re.fullmatch(r'[A-Za-z0-9!\"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~]+\s*', text):
        if _validate_base85(text):
            out.append(("base85", 85))
    
    # URL encoding
    if '%' in text and re.fullmatch(r'(%[0-9A-Fa-f]{2}|[A-Za-z0-9\-_.~:/?#\[\]@!$&\'()*+,;=])+', text):
        if _validate_url(text):
            out.append(("url", 90))
    
    # HTML entities
    if _validate_html_entity(text):
        out.append(("html_entity", 95))
    
    # JSON
    if (text.startswith('{') or text.startswith('[')) and _validate_json(text):
        out.append(("json", 90))
    
    # XML
    if _validate_xml(text):
        out.append(("xml", 90))
    
    # YAML
    if _validate_yaml(text):
        out.append(("yaml", 80))
    
    # JWT
    if _validate_jwt(text):
        out.append(("jwt", 95))
    
    # UUID
    if _validate_uuid(text):
        out.append(("uuid_parse", 95))
    
    # ULID
    if _validate_ulid(text):
        out.append(("ulid", 90))
    
    # Geohash
    if _validate_geohash(text):
        out.append(("geohash", 85))
    
    # MIME type
    if _validate_mimetype(text):
        out.append(("mime", 80))
    
    # Armor (PGP-style)
    if _validate_armor(text):
        out.append(("armor", 95))
    
    # Data URI
    if _validate_data_uri(text):
        out.append(("data_uri", 95))
    
    # Morse code
    if _validate_morse(text):
        out.append(("morse", 85))
    
    # Braille
    if _validate_braille(text):
        out.append(("braille", 95))
    
    # ROT13 (fallback for any ASCII text)
    if _validate_rot13(text):
        out.append(("rot13", 50))
    
    # Fullwidth
    if _validate_fullwidth(text):
        out.append(("fullwidth", 90))
    
    # Leetspeak
    if _validate_leet(text):
        out.append(("leet", 70))
    
    # Unicode escape
    if _validate_unicode_escape(text):
        out.append(("unicode_escape", 90))
    
    # Sort by confidence (highest first)
    out.sort(key=lambda x: -x[1])
    
    return [m[0] for m in out]


def detect_with_decode(engine, data: bytes) -> List[str]:
    """
    Detect encoding methods that can successfully decode the data.
    This actually tries to decode with each candidate to verify.
    """
    candidates = detect_candidates(data)
    valid = []
    
    for method_key in candidates:
        try:
            spec = engine.registry.get(method_key)
            if spec.decode is not None:
                # Try to decode
                decoded = spec.decode(data, {})
                # Check if decoded looks reasonable
                if decoded and _is_printable_utf8(decoded):
                    valid.append(method_key)
        except Exception:
            continue
    
    # If no valid methods found through decode test, return all candidates
    return valid if valid else candidates
