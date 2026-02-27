"""
Advanced Base-N and Binary Text Transform Encodings
Base36, Base91, Base122, Decimal, Nibble, Bit manipulation, and more
"""
from __future__ import annotations

from typing import Any

from ..models import MethodSpec


# =============================================================================
# BASE36 ENCODING (0-9, A-Z)
# =============================================================================
_BASE36_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base36_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Encode bytes to Base36 (0-9, A-Z)."""
    if not data:
        return b""
    value = int.from_bytes(data, "big")
    result = []
    while value > 0:
        value, rem = divmod(value, 36)
        result.append(_BASE36_ALPHABET[rem])
    # Handle leading zeros
    leading_zeros = len(data) - len(data.lstrip(b"\x00"))
    return (_BASE36_ALPHABET[0] * leading_zeros + "".join(reversed(result))).encode("ascii")


def base36_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode Base36 to bytes."""
    s = data.strip().decode("ascii").upper()
    if not s:
        return b""
    value = int(s, 36)
    byte_len = (value.bit_length() + 7) // 8
    return value.to_bytes(max(byte_len, 1), "big")


# =============================================================================
# BASE91 ENCODING (More efficient than Base64)
# =============================================================================
_BASE91_ALPHABET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&"
    "()*+,./:;<=>?@[]^_`{|}~\""
)


def base91_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes to Base91.
    More efficient than Base64 for binary data.
    """
    if not data:
        return b""
    
    result = []
    bit_buffer = 0
    bit_count = 0
    
    for byte in data:
        bit_buffer |= byte << bit_count
        bit_count += 8
        
        while bit_count > 13:
            val = bit_buffer & 0x1FFF
            if val > 88:
                bit_buffer >>= 13
                bit_count -= 13
            else:
                val = bit_buffer & 0xFFFF
                bit_buffer >>= 13
                bit_count -= 13
                result.append(_BASE91_ALPHABET[val % 91])
                val //= 91
            result.append(_BASE91_ALPHABET[val])
    
    if bit_count > 0:
        result.append(_BASE91_ALPHABET[bit_buffer & 0x1FFF])
        if bit_count > 7 or bit_buffer > 90:
            result.append(_BASE91_ALPHABET[(bit_buffer >> 13) & 0x1FFF])
    
    return "".join(result).encode("ascii")


def base91_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode Base91 to bytes."""
    s = data.strip().decode("ascii")
    if not s:
        return b""
    
    # Create reverse lookup
    reverse = {ch: i for i, ch in enumerate(_BASE91_ALPHABET)}
    
    result = bytearray()
    bit_buffer = 0
    bit_count = 0
    
    i = 0
    while i < len(s):
        if s[i] not in reverse:
            i += 1
            continue
            
        val = reverse[s[i]]
        bit_buffer |= val << bit_count
        bit_count += 13 if i + 1 < len(s) and s[i + 1] in reverse else 8
        i += 1
        
        while bit_count >= 8:
            result.append(bit_buffer & 0xFF)
            bit_buffer >>= 8
            bit_count -= 8
    
    return bytes(result)


# =============================================================================
# BASE122 ENCODING (Very compact)
# =============================================================================
_BASE122_ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "!#$%&()*+,-./:;<=>?@[]^_`{|}~"
)


def base122_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes to Base122.
    Very compact encoding for binary data.
    """
    if not data:
        return b""
    
    # Pad data to multiple of 16 bytes
    padding = (16 - (len(data) % 16)) % 16
    padded = data + b"\x00" * padding
    
    result = []
    for i in range(0, len(padded), 16):
        block = padded[i:i+16]
        # Convert 16 bytes to 122-base (approximately 13 chars)
        value = int.from_bytes(block, "big")
        block_result = []
        while value > 0:
            value, rem = divmod(value, 122)
            block_result.append(_BASE122_ALPHABET[rem])
        # Pad to fixed length
        block_result.extend(["0"] * (13 - len(block_result)))
        result.append("".join(reversed(block_result)))
    
    return "".join(result).encode("ascii")


def base122_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode Base122 to bytes."""
    s = data.strip().decode("ascii")
    if not s:
        return b""
    
    result = bytearray()
    # Process in chunks of 13 characters
    for i in range(0, len(s), 13):
        chunk = s[i:i+13]
        value = 0
        for ch in chunk:
            val = _BASE122_ALPHABET.index(ch) if ch in _BASE122_ALPHABET else 0
            value = value * 122 + val
        result.extend(value.to_bytes(16, "big"))
    
    # Remove padding (trailing zeros)
    return bytes(result).rstrip(b"\x00")


# =============================================================================
# DECIMAL ENCODING (Byte values as decimal numbers)
# =============================================================================
def decimal_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Encode bytes as decimal numbers separated by spaces."""
    sep = options.get("sep", " ")
    return sep.join(str(b) for b in data).encode("ascii")


def decimal_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode decimal numbers back to bytes."""
    text = data.decode("ascii", errors="ignore").strip()
    sep = options.get("sep", " ")
    parts = text.split(sep) if sep else text.split()
    return bytes(int(p) for p in parts if p.isdigit())


# =============================================================================
# NIBBLE ENCODING (4-bit values)
# =============================================================================
def nibble_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Encode bytes as nibble (4-bit) hex values."""
    result = []
    for byte in data:
        high = (byte >> 4) & 0x0F
        low = byte & 0x0F
        result.append(f"{high:X}{low:X}")
    sep = options.get("sep", "")
    return sep.join(result).encode("ascii")


def nibble_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode nibble values back to bytes."""
    text = data.decode("ascii", errors="ignore").replace(" ", "").replace("\n", "")
    result = []
    for i in range(0, len(text), 2):
        if i + 1 < len(text):
            nibble = int(text[i:i+2], 16)
            result.append(nibble)
    return bytes(result)


# =============================================================================
# BITSTRING ENCODING (Explicit binary with spaces)
# =============================================================================
def bitstring_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Encode bytes as explicit bitstring with optional spacing."""
    spacing = options.get("spacing", "byte")  # 'none', 'byte', 'nibble'
    
    if spacing == "none":
        return "".join(format(b, "08b") for b in data).encode("ascii")
    elif spacing == "nibble":
        result = []
        for byte in data:
            result.append(format(byte >> 4, "04b"))
            result.append(format(byte & 0x0F, "04b"))
        return " ".join(result).encode("ascii")
    else:  # byte spacing
        return " ".join(format(b, "08b") for b in data).encode("ascii")


def bitstring_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode bitstring back to bytes."""
    text = data.decode("ascii", errors="ignore").replace(" ", "")
    result = []
    for i in range(0, len(text), 8):
        if i + 8 <= len(text):
            result.append(int(text[i:i+8], 2))
    return bytes(result)


# =============================================================================
# BYTE SWAP / ENDIAN CONVERSION
# =============================================================================
def byteswap_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Swap byte order (endianness conversion)."""
    if len(data) % 2 != 0:
        data = data + b"\x00"  # Pad if odd
    result = bytearray()
    for i in range(0, len(data), 2):
        result.extend(data[i:i+2][::-1])
    return bytes(result)


def byteswap_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Swap bytes back (same operation)."""
    return byteswap_encode(data, options)


# =============================================================================
# ENDIAN SWAP (16-bit, 32-bit, 64-bit)
# =============================================================================
def endian_swap_16(data: bytes, options: dict[str, Any]) -> bytes:
    """Swap 16-bit word endianness."""
    result = bytearray()
    for i in range(0, len(data) - 1, 2):
        result.extend(data[i:i+2][::-1])
    if len(data) % 2:
        result.append(data[-1])
    return bytes(result)


def endian_swap_32(data: bytes, options: dict[str, Any]) -> bytes:
    """Swap 32-bit word endianness."""
    result = bytearray()
    for i in range(0, len(data) - 3, 4):
        result.extend(data[i:i+4][::-1])
    # Handle remaining bytes
    remaining = len(data) % 4
    if remaining:
        result.extend(data[-remaining:])
    return bytes(result)


def endian_swap_64(data: bytes, options: dict[str, Any]) -> bytes:
    """Swap 64-bit word endianness."""
    result = bytearray()
    for i in range(0, len(data) - 7, 8):
        result.extend(data[i:i+8][::-1])
    remaining = len(data) % 8
    if remaining:
        result.extend(data[-remaining:])
    return bytes(result)


# =============================================================================
# ASCII ARMOR (CRC24 based like PGP)
# =============================================================================
def ascii_armor_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Simple ASCII armor encoding (similar to PGP ASCII armor).
    Adds header, base64 content, and checksum.
    """
    import base64
    
    armor_type = options.get("type", "DATA")
    header = f"-----BEGIN PGP {armor_type}-----\n"
    footer = f"-----END PGP {armor_type}-----\n"
    
    encoded = base64.b64encode(data).decode("ascii")
    # Wrap at 76 characters
    wrapped = "\n".join(encoded[i:i+76] for i in range(0, len(encoded), 76))
    
    # Simple CRC24 checksum
    crc = 0xB704CE  # CRC24 init
    for byte in data:
        crc ^= byte << 16
        for _ in range(8):
            crc <<= 1
            if crc & 0x1000000:
                crc ^= 0x1864CFB
    crc &= 0xFFFFFF
    
    checksum = base64.b64encode(crc.to_bytes(3, "big")).decode("ascii")[:4]
    
    return f"{header}\n{wrapped}\n={checksum}\n{footer}".encode("ascii")


def ascii_armor_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode ASCII armor back to bytes."""
    import base64
    
    text = data.decode("ascii", errors="ignore")
    lines = text.strip().split("\n")
    
    # Find base64 content (between header and checksum)
    base64_lines = []
    in_content = False
    
    for line in lines:
        if line.startswith("-----BEGIN"):
            in_content = True
            continue
        if line.startswith("-----END"):
            break
        if line.startswith("="):
            break  # Skip checksum line
        if in_content and line.strip():
            base64_lines.append(line.strip())
    
    if not base64_lines:
        raise ValueError("No base64 content found in ASCII armor")
    
    base64_data = "".join(base64_lines)
    return base64.b64decode(base64_data)


# =============================================================================
# RUN-LENGTH ENCODING (RLE)
# =============================================================================
def rle_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Run-length encoding for compressing repeated bytes.
    Format: [count][byte] pairs
    """
    if not data:
        return b""
    
    result = bytearray()
    i = 0
    while i < len(data):
        byte = data[i]
        count = 1
        while i + count < len(data) and data[i + count] == byte and count < 255:
            count += 1
        result.append(count)
        result.append(byte)
        i += count
    
    return bytes(result)


def rle_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode run-length encoded data."""
    result = bytearray()
    i = 0
    while i + 1 < len(data):
        count = data[i]
        byte = data[i + 1]
        result.extend([byte] * count)
        i += 2
    return bytes(result)


# =============================================================================
# DELTA ENCODING (Difference between consecutive bytes)
# =============================================================================
def delta_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Delta encoding: store differences between consecutive bytes.
    First byte is stored as-is.
    """
    if not data:
        return b""
    
    result = bytearray([data[0]])
    for i in range(1, len(data)):
        diff = (data[i] - data[i-1]) % 256
        result.append(diff)
    
    return bytes(result)


def delta_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode delta-encoded data."""
    if not data:
        return b""
    
    result = bytearray([data[0]])
    for i in range(1, len(data)):
        byte = (result[-1] + data[i]) % 256
        result.append(byte)
    
    return bytes(result)


# =============================================================================
# XOR ENCODING (Simple XOR with key)
# =============================================================================
def xor_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Simple XOR encoding with a key."""
    key = options.get("key", "secret").encode("utf-8")
    if not key:
        key = b"\x00"
    
    result = bytearray()
    for i, byte in enumerate(data):
        result.append(byte ^ key[i % len(key)])
    
    return bytes(result)


def xor_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """XOR decoding (same as encoding)."""
    return xor_encode(data, options)


# =============================================================================
# ROT FAMILY (ROT47, ROT13, etc.)
# =============================================================================
def rot47_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """ROT47 encoding (7-bit ASCII rotation)."""
    text = data.decode("ascii", errors="ignore")
    result = []
    for ch in text:
        code = ord(ch)
        if 33 <= code <= 126:
            result.append(chr(33 + ((code - 33 + 47) % 94)))
        else:
            result.append(ch)
    return "".join(result).encode("ascii")


def rot47_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """ROT47 decoding (same as encoding due to symmetry)."""
    return rot47_encode(data, options)


def get_specs() -> list[MethodSpec]:
    return [
        # Base-N variants
        MethodSpec("base36", "advanced_base_n", "Base36 (0-9, A-Z)", base36_encode, base36_decode, aliases=("b36",)),
        MethodSpec("base91", "advanced_base_n", "Base91 (more efficient than Base64)", base91_encode, base91_decode, aliases=("b91",)),
        MethodSpec("base122", "advanced_base_n", "Base122 (very compact)", base122_encode, base122_decode, aliases=("b122",)),
        
        # Numeric representations
        MethodSpec("decimal", "advanced_base_n", "Decimal byte values", decimal_encode, decimal_decode, aliases=("dec", "base10")),
        MethodSpec("nibble", "advanced_base_n", "Nibble (4-bit) hex", nibble_encode, nibble_decode),
        MethodSpec("bitstring", "advanced_base_n", "Explicit bitstring", bitstring_encode, bitstring_decode, aliases=("bits",)),
        
        # Byte manipulation
        MethodSpec("byteswap", "advanced_base_n", "Swap byte order", byteswap_encode, byteswap_decode, aliases=("swap",)),
        MethodSpec("endian16", "advanced_base_n", "16-bit endian swap", endian_swap_16, endian_swap_16),
        MethodSpec("endian32", "advanced_base_n", "32-bit endian swap", endian_swap_32, endian_swap_32),
        MethodSpec("endian64", "advanced_base_n", "64-bit endian swap", endian_swap_64, endian_swap_64),
        
        # Encoding formats
        MethodSpec("ascii_armor", "advanced_base_n", "ASCII armor (PGP-style)", ascii_armor_encode, ascii_armor_decode, aliases=("pgp_armor",)),
        
        # Simple compression
        MethodSpec("rle", "advanced_base_n", "Run-length encoding", rle_encode, rle_decode),
        MethodSpec("delta", "advanced_base_n", "Delta encoding", delta_encode, delta_decode),
        
        # Simple encryption
        MethodSpec("xor", "advanced_base_n", "XOR with key", xor_encode, xor_decode),
        
        # ROT family
        MethodSpec("rot47", "advanced_base_n", "ROT47 (7-bit ASCII)", rot47_encode, rot47_decode),
    ]
