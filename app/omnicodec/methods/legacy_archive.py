"""
Legacy & Archive Encodings
BinHex, XXEncode, yEnc, TAR, and other legacy formats
"""
from __future__ import annotations

import struct
from typing import Any

from ..models import MethodSpec


def _to_text(data: bytes, options: dict[str, Any]) -> str:
    return data.decode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


def _to_bytes(text: str, options: dict[str, Any]) -> bytes:
    return text.encode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


# =============================================================================
# BINHEX ENCODING (Macintosh legacy)
# =============================================================================
def binhex_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    BinHex encoding (Macintosh legacy format).
    Uses ASCII characters to represent binary data.
    """
    if not data:
        return b""
    
    # Simplified BinHex 4.0 encoding
    # Real BinHex includes Mac resource forks and CRC
    result = bytearray()
    
    # Add header
    result.extend(b"BinHex 4.0 File\n")
    
    # Encode data using ASCII-safe encoding
    for byte in data:
        if 33 <= byte <= 126 and byte not in (92, 96):  # Exclude \ and `
            result.append(byte)
        else:
            # Escape special characters
            result.append(90)  # 'Z' as escape
            result.append(byte ^ 0x80)
    
    return bytes(result)


def binhex_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode BinHex format.
    """
    text = _to_text(data, options)
    
    # Skip header if present
    if text.startswith("BinHex"):
        newline_pos = text.find("\n")
        if newline_pos != -1:
            text = text[newline_pos + 1:]
    
    result = bytearray()
    i = 0
    while i < len(text):
        ch = ord(text[i])
        if ch == 90:  # 'Z' escape
            if i + 1 < len(text):
                result.append(ord(text[i + 1]) ^ 0x80)
                i += 2
            else:
                i += 1
        elif 33 <= ch <= 126 and ch not in (92, 96):
            result.append(ch)
            i += 1
        else:
            i += 1
    
    return bytes(result)


# =============================================================================
# XXENCODE ENCODING
# =============================================================================
XXENCODE_CHARS = "+-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def xxencode_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    XXEncode encoding (improved UUEncode).
    Uses all alphanumeric characters plus + and -.
    """
    if not data:
        return b""
    
    result = bytearray()
    line_length = int(options.get("line_length", 45))
    
    for i in range(0, len(data), 3):
        chunk = data[i:i+3]
        
        # Encode 3 bytes into 4 characters
        b1 = chunk[0] if len(chunk) > 0 else 0
        b2 = chunk[1] if len(chunk) > 1 else 0
        b3 = chunk[2] if len(chunk) > 2 else 0
        
        c1 = (b1 >> 2) & 0x3F
        c2 = ((b1 << 4) | (b2 >> 4)) & 0x3F
        c3 = ((b2 << 2) | (b3 >> 6)) & 0x3F
        c4 = b3 & 0x3F
        
        result.extend([
            ord(XXENCODE_CHARS[c1]),
            ord(XXENCODE_CHARS[c2]),
            ord(XXENCODE_CHARS[c3]),
            ord(XXENCODE_CHARS[c4]),
        ])
        
        # Add newline every line_length encoded bytes
        if ((i // 3) + 1) * 4 % line_length == 0:
            result.extend(b"\n")
    
    return bytes(result)


def xxencode_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode XXEncode format.
    """
    text = _to_text(data, options)
    
    # Create reverse lookup
    reverse = {ch: i for i, ch in enumerate(XXENCODE_CHARS)}
    
    result = bytearray()
    chars = [ch for ch in text if ch in XXENCODE_CHARS]
    
    for i in range(0, len(chars) - 3, 4):
        c1 = reverse.get(chars[i], 0)
        c2 = reverse.get(chars[i+1], 0)
        c3 = reverse.get(chars[i+2], 0)
        c4 = reverse.get(chars[i+3], 0)
        
        b1 = (c1 << 2) | (c2 >> 4)
        b2 = ((c2 & 0x0F) << 4) | (c3 >> 2)
        b3 = ((c3 & 0x03) << 6) | c4
        
        result.extend([b1, b2, b3])
    
    return bytes(result)


# =============================================================================
# YENC ENCODING (Usenet binary encoding)
# =============================================================================
def yenc_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    yEnc encoding (efficient Usenet binary encoding).
    """
    if not data:
        return b""
    
    result = bytearray()
    
    # yEnc header
    filename = options.get("filename", "data.bin")
    result.extend(f"=ybegin line=128 size={len(data)} name={filename}\n".encode("ascii"))
    
    # Encode data
    line_pos = 0
    for byte in data:
        # yEnc encoding: (byte - 42) % 256
        encoded = (byte - 42) % 256
        
        # Escape special characters
        if encoded in (0, 9, 10, 13, 61, 92):
            result.append(92)  # '=' escape
            encoded = (encoded + 64) % 256
        
        result.append(encoded)
        line_pos += 1
        
        if line_pos >= 128:
            result.append(10)  # Newline
            line_pos = 0
    
    # yEnc trailer
    import zlib
    crc = zlib.crc32(data) & 0xFFFFFFFF
    result.extend(f"\n=yend size={len(data)} part=1 crc32={crc:08x}".encode("ascii"))
    
    return bytes(result)


def yenc_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode yEnc format.
    """
    text = _to_text(data, options)
    
    # Find data between header and trailer
    begin_pos = text.find("=ybegin")
    end_pos = text.find("=yend")
    
    if begin_pos == -1:
        begin_pos = 0
    else:
        # Find end of header line
        begin_pos = text.find("\n", begin_pos)
        if begin_pos != -1:
            begin_pos += 1
    
    if end_pos == -1:
        end_pos = len(text)
    
    encoded_data = text[begin_pos:end_pos]
    
    result = bytearray()
    i = 0
    while i < len(encoded_data):
        ch = ord(encoded_data[i])
        
        if ch == 10 or ch == 13:  # Skip newlines
            i += 1
            continue
        
        if ch == 92:  # Escape character
            if i + 1 < len(encoded_data):
                ch = ord(encoded_data[i + 1])
                ch = (ch - 64) % 256
                i += 2
            else:
                i += 1
                continue
        
        # Decode: (byte + 42) % 256
        decoded = (ch + 42) % 256
        result.append(decoded)
        i += 1
    
    return bytes(result)


# =============================================================================
# TAR ARCHIVE ENCODING (Single file)
# =============================================================================
def tar_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Create a minimal TAR archive from data.
    """
    filename = options.get("filename", "data.txt").encode("utf-8")[:100]
    
    # TAR header (512 bytes)
    header = bytearray(512)
    
    # File name (0-99)
    header[0:len(filename)] = filename
    
    # File mode (100-107)
    header[100:108] = b"0000644\x00"
    
    # UID (108-115)
    header[108:116] = b"0001750\x00"
    
    # GID (116-123)
    header[116:124] = b"0001750\x00"
    
    # File size in octal (124-135)
    size_octal = f"{len(data):011o}\x00".encode("ascii")
    header[124:136] = size_octal
    
    # Modification time (136-147)
    import time
    mtime = int(time.time())
    mtime_octal = f"{mtime:011o}\x00".encode("ascii")
    header[136:148] = mtime_octal
    
    # Checksum placeholder (148-156)
    header[148:156] = b"        "  # 8 spaces
    
    # Type flag (156) - regular file
    header[156] = ord("0")
    
    # Magic (257-262)
    header[257:263] = b"ustar\x00"
    
    # Version (263-264)
    header[263:265] = b"00"
    
    # Calculate checksum
    checksum = sum(header)
    checksum_octal = f"{checksum:06o}\x00".encode("ascii")
    header[148:156] = checksum_octal
    
    # Pad data to multiple of 512
    padded_data = data
    if len(data) % 512 != 0:
        padded_data = data + b"\x00" * (512 - len(data) % 512)
    
    # End of archive (two 512-byte zero blocks)
    end_blocks = b"\x00" * 1024
    
    return bytes(header) + padded_data + end_blocks


def tar_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Extract file content from TAR archive.
    """
    if len(data) < 512:
        raise ValueError("Data too small for TAR")
    
    # Parse header
    header = data[:512]
    
    # Check for valid TAR (magic at offset 257)
    if header[257:263] != b"ustar\x00":
        # Not a valid TAR, return data as-is
        return data
    
    # Extract file size (octal string at offset 124)
    size_str = header[124:136].rstrip(b"\x00").decode("ascii", errors="ignore")
    try:
        file_size = int(size_str, 8)
    except ValueError:
        file_size = 0
    
    # Extract file content
    content_start = 512
    content_end = content_start + file_size
    
    return data[content_start:content_end]


# =============================================================================
# MIME BASE64 ENCODING (with headers)
# =============================================================================
def mime_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data with MIME Base64 headers.
    """
    import base64
    
    content_type = options.get("content_type", "text/plain")
    charset = options.get("charset", "utf-8")
    transfer_encoding = options.get("transfer_encoding", "base64")
    
    encoded = base64.b64encode(data).decode("ascii")
    
    # Wrap at 76 characters (MIME standard)
    wrapped = "\n".join(encoded[i:i+76] for i in range(0, len(encoded), 76))
    
    mime_message = f"""Content-Type: {content_type}; charset={charset}
Content-Transfer-Encoding: {transfer_encoding}

{wrapped}
"""
    return mime_message.encode("ascii")


def mime_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode MIME Base64 message.
    """
    import base64
    
    text = _to_text(data, options)
    
    # Find empty line separating headers from body
    parts = text.split("\n\n", 1)
    if len(parts) == 2:
        body = parts[1]
    else:
        body = text
    
    # Remove whitespace and decode Base64
    body = "".join(body.split())
    
    try:
        return base64.b64decode(body)
    except Exception:
        return body.encode("utf-8")


# =============================================================================
# NETBIN ENCODING (Simple binary-to-text)
# =============================================================================
def netbin_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    NetBin encoding (simple binary to text).
    """
    result = bytearray()
    
    # Header
    result.extend(b"NB01")
    result.extend(f"{len(data):08x}".encode("ascii"))
    
    # Encode data as hex pairs
    for byte in data:
        result.append(65 + (byte >> 4))  # High nibble -> A-P
        result.append(65 + (byte & 0x0F))  # Low nibble -> A-P
    
    return bytes(result)


def netbin_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode NetBin format.
    """
    text = _to_text(data, options)
    
    if not text.startswith("NB01"):
        raise ValueError("Invalid NetBin header")
    
    # Extract length
    length_str = text[4:12]
    try:
        length = int(length_str, 16)
    except ValueError:
        length = len(text) - 12
    
    # Decode
    result = bytearray()
    for i in range(12, len(text) - 1, 2):
        high = ord(text[i]) - 65
        low = ord(text[i + 1]) - 65
        if 0 <= high <= 15 and 0 <= low <= 15:
            result.append((high << 4) | low)
    
    return bytes(result[:length])


# =============================================================================
# ARMOR ENCODING (Generic)
# =============================================================================
def armor_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Generic armor encoding (PGP-style).
    """
    import base64
    
    armor_type = options.get("type", "OMNICODEC")
    
    encoded = base64.b64encode(data).decode("ascii")
    wrapped = "\n".join(encoded[i:i+64] for i in range(0, len(encoded), 64))
    
    # Calculate CRC24
    crc = 0xB704CE
    for byte in data:
        crc ^= byte << 16
        for _ in range(8):
            crc <<= 1
            if crc & 0x1000000:
                crc ^= 0x1864CFB
    crc &= 0xFFFFFF
    
    crc_encoded = base64.b64encode(crc.to_bytes(3, "big")).decode("ascii")[:4]
    
    return f"-----BEGIN {armor_type}-----\n{wrapped}\n={crc_encoded}\n-----END {armor_type}-----\n".encode("ascii")


def armor_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode generic armor format.
    """
    import base64
    
    text = _to_text(data, options)
    
    # Find content between BEGIN and END
    begin_pos = text.find("-----BEGIN")
    end_pos = text.find("-----END")
    
    if begin_pos == -1 or end_pos == -1:
        return data
    
    # Extract base64 content
    content_start = text.find("\n", begin_pos) + 1
    content_end = text.find("=", content_start)
    
    if content_end == -1:
        content_end = end_pos
    
    base64_content = text[content_start:content_end].replace("\n", "")
    
    try:
        return base64.b64decode(base64_content)
    except Exception:
        return base64_content.encode("utf-8")


def get_specs() -> list[MethodSpec]:
    return [
        # Legacy Mac/Usenet
        MethodSpec("binhex", "legacy_archive", "BinHex (Macintosh legacy)", binhex_encode, binhex_decode),
        MethodSpec("xxencode", "legacy_archive", "XXEncode", xxencode_encode, xxencode_decode, aliases=("xx",)),
        MethodSpec("yenc", "legacy_archive", "yEnc (Usenet)", yenc_encode, yenc_decode),
        
        # Archive formats
        MethodSpec("tar", "legacy_archive", "TAR archive (single file)", tar_encode, tar_decode),
        
        # Email/MIME
        MethodSpec("mime", "legacy_archive", "MIME Base64 with headers", mime_encode, mime_decode),
        
        # Generic armor
        MethodSpec("armor", "legacy_archive", "Generic armor (PGP-style)", armor_encode, armor_decode),
        
        # Simple encodings
        MethodSpec("netbin", "legacy_archive", "NetBin encoding", netbin_encode, netbin_decode),
    ]
