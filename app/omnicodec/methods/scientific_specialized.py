"""
Scientific & Specialized Encodings
UUID, ULID, NanoID, CUID, Geohash, Plus Code, Snowflake, and more
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any

from ..models import MethodSpec


def _to_text(data: bytes, options: dict[str, Any]) -> str:
    return data.decode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


def _to_bytes(text: str, options: dict[str, Any]) -> bytes:
    return text.encode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


# =============================================================================
# UUID ENCODING (Various versions)
# =============================================================================
import uuid as uuid_module


def uuid4_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Generate UUID v4 (random) based on input data as seed.
    """
    # Use input data to seed random
    seed = int.from_bytes(hashlib.sha256(data).digest()[:16], "big")
    random.seed(seed)
    
    # Generate random bytes for UUID
    random_bytes = bytes([random.randint(0, 255) for _ in range(16)])
    
    # Set version to 4
    random_bytes = random_bytes[:6] + bytes([0x40 | (random_bytes[6] & 0x0F)]) + random_bytes[7:]
    # Set variant to RFC 4122
    random_bytes = random_bytes[:8] + bytes([0x80 | (random_bytes[8] & 0x3F)]) + random_bytes[9:]
    
    u = uuid_module.UUID(bytes=random_bytes)
    return str(u).encode("ascii")


def uuid4_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Extract bytes from UUID.
    """
    text = _to_text(data, options).strip()
    u = uuid_module.UUID(text)
    return u.bytes


def uuid1_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Generate UUID v1 (time-based) with node from data.
    """
    # Use hash of data as node ID
    node_hash = hashlib.sha256(data).digest()[:6]
    node = int.from_bytes(node_hash, "big")
    
    # Generate UUID v1
    u = uuid_module.uuid1(node=node)
    return str(u).encode("ascii")


def uuid1_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Extract timestamp and node from UUID v1.
    """
    text = _to_text(data, options).strip()
    u = uuid_module.UUID(text)
    # Return node bytes
    return u.node.to_bytes(6, "big")


def uuid3_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Generate UUID v3 (MD5-based) from data.
    """
    namespace = options.get("namespace", "dns")
    ns_map = {
        "dns": uuid_module.NAMESPACE_DNS,
        "url": uuid_module.NAMESPACE_URL,
        "oid": uuid_module.NAMESPACE_OID,
        "x500": uuid_module.NAMESPACE_X500,
    }
    ns = ns_map.get(namespace, uuid_module.NAMESPACE_DNS)
    
    u = uuid_module.uuid3(ns, _to_text(data, options))
    return str(u).encode("ascii")


def uuid5_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Generate UUID v5 (SHA1-based) from data.
    """
    namespace = options.get("namespace", "dns")
    ns_map = {
        "dns": uuid_module.NAMESPACE_DNS,
        "url": uuid_module.NAMESPACE_URL,
        "oid": uuid_module.NAMESPACE_OID,
        "x500": uuid_module.NAMESPACE_X500,
    }
    ns = ns_map.get(namespace, uuid_module.NAMESPACE_DNS)
    
    u = uuid_module.uuid5(ns, _to_text(data, options))
    return str(u).encode("ascii")


# =============================================================================
# ULID ENCODING (Universally Unique Lexicographically Sortable Identifier)
# =============================================================================
ULID_CHARS = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def ulid_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Generate ULID from data.
    ULID = 48-bit timestamp + 80-bit random
    """
    # Use input hash as randomness source
    hash_bytes = hashlib.sha256(data).digest()
    
    # Current timestamp (or from options)
    timestamp = int(options.get("timestamp", time.time() * 1000)) & 0xFFFFFFFFFFFF
    
    # Encode timestamp (10 chars in base32)
    result = []
    ts = timestamp
    for _ in range(10):
        result.append(ULID_CHARS[ts & 0x1F])
        ts >>= 5
    timestamp_part = "".join(reversed(result))
    
    # Encode randomness from hash (16 chars in base32)
    result = []
    rand = int.from_bytes(hash_bytes[:10], "big")
    for _ in range(16):
        result.append(ULID_CHARS[rand & 0x1F])
        rand >>= 5
    random_part = "".join(reversed(result))
    
    return (timestamp_part + random_part).encode("ascii")


def ulid_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode ULID and extract timestamp and randomness.
    """
    text = _to_text(data, options).upper()
    
    if len(text) != 26:
        raise ValueError("Invalid ULID length")
    
    # Decode timestamp
    timestamp = 0
    for ch in text[:10]:
        if ch in ULID_CHARS:
            timestamp = (timestamp << 5) | ULID_CHARS.index(ch)
    
    return timestamp.to_bytes(6, "big")


# =============================================================================
# NANOID ENCODING
# =============================================================================
NANOID_ALPHABET = "_-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def nanoid_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Generate NanoID from data.
    """
    size = int(options.get("size", 21))
    
    # Use hash as seed
    hash_bytes = hashlib.sha256(data).digest()
    
    result = []
    hash_idx = 0
    for _ in range(size):
        if hash_idx >= len(hash_bytes):
            hash_bytes = hashlib.sha256(hash_bytes).digest()
            hash_idx = 0
        
        idx = hash_bytes[hash_idx] % len(NANOID_ALPHABET)
        result.append(NANOID_ALPHABET[idx])
        hash_idx += 1
    
    return "".join(result).encode("ascii")


def nanoid_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    NanoID decode returns hash of the ID (one-way).
    """
    text = _to_text(data, options)
    return hashlib.sha256(text.encode()).digest()


# =============================================================================
# CUID ENCODING (Cluster-Unique ID)
# =============================================================================
def cuid_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Generate CUID-like identifier from data.
    Format: c + timestamp + counter + random + hash
    """
    timestamp = int(time.time() * 1000)
    counter = random.randint(0, 0xFFFF)
    
    # Hash of data
    data_hash = hashlib.sha256(data).hexdigest()[:8]
    
    # Build CUID
    cuid = f"c{timestamp:x}{counter:04x}{data_hash}"
    return cuid.encode("ascii")


def cuid_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Extract data hash from CUID.
    """
    text = _to_text(data, options)
    if text.startswith("c") and len(text) >= 24:
        # Extract last 8 chars (hash portion)
        return text[-8:].encode("ascii")
    return text.encode("utf-8")


# =============================================================================
# SNOWFLAKE ID (Twitter-style distributed ID)
# =============================================================================
def snowflake_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Generate Snowflake-style ID.
    Format: timestamp(41) + machine_id(10) + sequence(12)
    """
    # Custom epoch
    epoch = int(options.get("epoch", 1288834974657))  # Twitter epoch
    timestamp = int(time.time() * 1000) - epoch
    
    # Machine ID from data hash
    machine_hash = hashlib.sha256(data).digest()
    machine_id = int.from_bytes(machine_hash[:2], "big") & 0x3FF
    
    # Sequence number
    sequence = random.randint(0, 0xFFF)
    
    # Build 64-bit ID
    snowflake_id = (timestamp << 22) | (machine_id << 12) | sequence
    
    return str(snowflake_id).encode("ascii")


def snowflake_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Parse Snowflake ID components.
    """
    text = _to_text(data, options)
    snowflake_id = int(text)
    
    # Extract components
    sequence = snowflake_id & 0xFFF
    machine_id = (snowflake_id >> 12) & 0x3FF
    timestamp = (snowflake_id >> 22) & 0x1FFFFFFFFFF
    
    # Return as bytes
    return timestamp.to_bytes(6, "big") + machine_id.to_bytes(2, "big") + sequence.to_bytes(2, "big")


# =============================================================================
# GEOHASH ENCODING
# =============================================================================
GEOHASH_CHARS = "0123456789bcdefghjkmnpqrstuvwxyz"


def geohash_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode coordinates as Geohash.
    Input format: "lat,lon" or bytes interpreted as such.
    """
    text = _to_text(data, options)
    
    # Parse coordinates
    if "," in text:
        parts = text.split(",")
        lat = float(parts[0])
        lon = float(parts[1])
    else:
        # Use hash to generate pseudo-coordinates
        hash_bytes = hashlib.sha256(data).digest()
        lat = (int.from_bytes(hash_bytes[:4], "big") % 18000) / 100 - 90
        lon = (int.from_bytes(hash_bytes[4:8], "big") % 36000) / 100 - 180
    
    precision = int(options.get("precision", 8))
    
    # Encode as geohash
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]
    
    geohash = []
    bit = 0
    ch = 0
    is_lon = True
    
    while len(geohash) < precision:
        if is_lon:
            mid = (lon_range[0] + lon_range[1]) / 2
            if lon >= mid:
                ch |= (1 << (4 - bit))
                lon_range[0] = mid
            else:
                lon_range[1] = mid
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat >= mid:
                ch |= (1 << (4 - bit))
                lat_range[0] = mid
            else:
                lat_range[1] = mid
        
        is_lon = not is_lon
        bit += 1
        
        if bit == 5:
            geohash.append(GEOHASH_CHARS[ch])
            bit = 0
            ch = 0
    
    return "".join(geohash).encode("ascii")


def geohash_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode Geohash to coordinates.
    """
    text = _to_text(data, options).lower()
    
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]
    
    is_lon = True
    
    for ch in text:
        if ch not in GEOHASH_CHARS:
            continue
        
        val = GEOHASH_CHARS.index(ch)
        for i in range(4, -1, -1):
            bit = (val >> i) & 1
            if is_lon:
                mid = (lon_range[0] + lon_range[1]) / 2
                if bit:
                    lon_range[0] = mid
                else:
                    lon_range[1] = mid
            else:
                mid = (lat_range[0] + lat_range[1]) / 2
                if bit:
                    lat_range[0] = mid
                else:
                    lat_range[1] = mid
            is_lon = not is_lon
    
    lat = (lat_range[0] + lat_range[1]) / 2
    lon = (lon_range[0] + lon_range[1]) / 2
    
    return f"{lat:.6f},{lon:.6f}".encode("ascii")


# =============================================================================
# PLUS CODE (Open Location Code)
# =============================================================================
PLUS_CODE_CHARS = "23456789CFGHJMPQRVWX"


def plus_code_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode as Plus Code (Open Location Code).
    Similar to Geohash but designed for street addresses.
    """
    # Use hash to generate pseudo-coordinates
    hash_bytes = hashlib.sha256(data).digest()
    lat = (int.from_bytes(hash_bytes[:4], "big") % 18000) / 100 - 90
    lon = (int.from_bytes(hash_bytes[4:8], "big") % 36000) / 100 - 180
    
    # Simplified Plus Code encoding
    lat *= 8000
    lon *= 8000
    
    result = []
    for _ in range(8):
        lat_idx = int(lat) % len(PLUS_CODE_CHARS)
        lon_idx = int(lon) % len(PLUS_CODE_CHARS)
        result.append(PLUS_CODE_CHARS[lon_idx])
        result.append(PLUS_CODE_CHARS[lat_idx])
        lat //= len(PLUS_CODE_CHARS)
        lon //= len(PLUS_CODE_CHARS)
    
    # Add + separator
    result.insert(8, "+")
    
    return "".join(result).encode("ascii")


def plus_code_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode Plus Code to coordinates.
    """
    text = _to_text(data, options).upper().replace("+", "")
    
    lat = 0
    lon = 0
    scale = 1
    
    for i, ch in enumerate(text[:8]):
        if ch not in PLUS_CODE_CHARS:
            continue
        idx = PLUS_CODE_CHARS.index(ch)
        if i % 2 == 0:
            lon += idx * scale
        else:
            lat += idx * scale
        scale *= len(PLUS_CODE_CHARS)
    
    lat_deg = lat / 8000 - 90
    lon_deg = lon / 8000 - 180
    
    return f"{lat_deg:.6f},{lon_deg:.6f}".encode("ascii")


# =============================================================================
# BASE32HEX ENCODING (RFC 4648)
# =============================================================================
def base32hex_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Base32hex encoding (RFC 4648).
    Uses 0-9, A-V instead of A-Z, 2-7.
    """
    import base64
    return base64.b32hexencode(data)


def base32hex_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode Base32hex.
    """
    import base64
    return base64.b32hexdecode(data, casefold=True)


# =============================================================================
# CROCKFORD BASE32 ENCODING
# =============================================================================
CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def crockford_base32_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Crockford's Base32 encoding.
    Optimized for human use (excludes similar-looking characters).
    """
    if not data:
        return b""
    
    value = int.from_bytes(data, "big")
    result = []
    
    while value > 0:
        value, idx = divmod(value, 32)
        result.append(CROCKFORD_ALPHABET[idx])
    
    # Handle leading zeros
    leading_zeros = len(data) - len(data.lstrip(b"\x00"))
    result.extend([CROCKFORD_ALPHABET[0]] * leading_zeros)
    
    return "".join(reversed(result)).encode("ascii")


def crockford_base32_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode Crockford's Base32.
    """
    text = _to_text(data, options).upper().replace("O", "0").replace("I", "1").replace("L", "1")
    
    if not text:
        return b""
    
    value = 0
    for ch in text:
        if ch in CROCKFORD_ALPHABET:
            value = value * 32 + CROCKFORD_ALPHABET.index(ch)
    
    byte_len = (value.bit_length() + 7) // 8
    return value.to_bytes(max(byte_len, 1), "big")


def get_specs() -> list[MethodSpec]:
    return [
        # UUID family
        MethodSpec("uuid1", "scientific_specialized", "UUID v1 (time-based)", uuid1_encode, uuid1_decode),
        MethodSpec("uuid3", "scientific_specialized", "UUID v3 (MD5-based)", uuid3_encode, None),
        MethodSpec("uuid4", "scientific_specialized", "UUID v4 (random)", uuid4_encode, uuid4_decode),
        MethodSpec("uuid5", "scientific_specialized", "UUID v5 (SHA1-based)", uuid5_encode, None),
        
        # Modern IDs
        MethodSpec("ulid", "scientific_specialized", "ULID (sortable unique ID)", ulid_encode, ulid_decode),
        MethodSpec("nanoid", "scientific_specialized", "NanoID", nanoid_encode, nanoid_decode),
        MethodSpec("cuid", "scientific_specialized", "CUID (cluster-unique ID)", cuid_encode, cuid_decode),
        MethodSpec("snowflake", "scientific_specialized", "Snowflake ID", snowflake_encode, snowflake_decode),
        
        # Geographic
        MethodSpec("geohash", "scientific_specialized", "Geohash coordinates", geohash_encode, geohash_decode),
        MethodSpec("plus_code", "scientific_specialized", "Plus Code (Open Location)", plus_code_encode, plus_code_decode),
        
        # Base32 variants
        MethodSpec("base32hex", "scientific_specialized", "Base32hex (RFC 4648)", base32hex_encode, base32hex_decode),
        MethodSpec("crockford_base32", "scientific_specialized", "Crockford Base32", crockford_base32_encode, crockford_base32_decode),
    ]
