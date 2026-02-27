"""
Advanced Serialization Encodings
YAML, MessagePack, CBOR, BSON, Protobuf-style, and more
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
# YAML ENCODING
# =============================================================================
def yaml_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data as YAML.
    Simple YAML format without external dependencies.
    """
    text = _to_text(data, options)
    # Simple YAML representation
    # Escape special YAML characters
    escaped = text.replace("|", "\\|").replace(">", "\\>").replace("'", "''")
    
    # Use literal block scalar for multiline
    if "\n" in escaped:
        return f"data: |\n  {escaped.replace(chr(10), chr(10) + '  ')}\n".encode("utf-8")
    else:
        return f'data: "{escaped}"\n'.encode("utf-8")


def yaml_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode YAML and extract data.
    Simple parser for our YAML format.
    """
    text = _to_text(data, options)
    
    # Look for data: key
    if "data:" in text:
        # Extract value after data:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("data:"):
                value = line[5:].strip()
                if value.startswith("|"):
                    # Literal block
                    block_lines = []
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith("  "):
                            block_lines.append(lines[j][2:])
                        elif lines[j].strip() == "":
                            continue
                        else:
                            break
                    return "\n".join(block_lines).encode("utf-8")
                elif value.startswith('"') and value.endswith('"'):
                    return value[1:-1].encode("utf-8")
                elif value.startswith("'") and value.endswith("'"):
                    return value[1:-1].encode("utf-8")
                else:
                    return value.encode("utf-8")
    
    return text.encode("utf-8")


# =============================================================================
# MESSAGEPACK ENCODING (Simplified)
# =============================================================================
def msgpack_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data in MessagePack-like binary format.
    Simplified implementation without external dependencies.
    """
    # MessagePack format for bin8: 0xC4 + length + data
    length = len(data)
    
    if length < 256:
        # bin8 format
        return bytes([0xC4, length]) + data
    elif length < 65536:
        # bin16 format
        return bytes([0xC5]) + struct.pack(">H", length) + data
    else:
        # bin32 format
        return bytes([0xC6]) + struct.pack(">I", length) + data


def msgpack_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode MessagePack binary format.
    """
    if len(data) < 2:
        raise ValueError("Invalid MessagePack data")
    
    format_byte = data[0]
    
    if format_byte == 0xC4:  # bin8
        length = data[1]
        return data[2:2+length]
    elif format_byte == 0xC5:  # bin16
        length = struct.unpack(">H", data[1:3])[0]
        return data[3:3+length]
    elif format_byte == 0xC6:  # bin32
        length = struct.unpack(">I", data[1:5])[0]
        return data[5:5+length]
    else:
        raise ValueError(f"Unknown MessagePack format: {format_byte:#x}")


# =============================================================================
# CBOR ENCODING (Concise Binary Object Representation)
# =============================================================================
def cbor_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data in CBOR format.
    Simplified implementation for byte strings.
    """
    length = len(data)
    
    # CBOR major type 2 (byte string) + additional info
    if length < 24:
        return bytes([0x40 + length]) + data
    elif length < 256:
        return bytes([0x58, length]) + data
    elif length < 65536:
        return bytes([0x59]) + struct.pack(">H", length) + data
    else:
        return bytes([0x5A]) + struct.pack(">I", length) + data


def cbor_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode CBOR byte string.
    """
    if len(data) < 1:
        raise ValueError("Invalid CBOR data")
    
    first_byte = data[0]
    major_type = (first_byte >> 5) & 0x07
    additional = first_byte & 0x1F
    
    if major_type != 2:
        raise ValueError(f"Expected byte string (major type 2), got {major_type}")
    
    if additional < 24:
        length = additional
        offset = 1
    elif additional == 24:
        length = data[1]
        offset = 2
    elif additional == 25:
        length = struct.unpack(">H", data[1:3])[0]
        offset = 3
    elif additional == 26:
        length = struct.unpack(">I", data[1:5])[0]
        offset = 5
    else:
        raise ValueError(f"Invalid CBOR additional info: {additional}")
    
    return data[offset:offset+length]


# =============================================================================
# BSON ENCODING (Binary JSON - Simplified)
# =============================================================================
def bson_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data in BSON-like format.
    Simplified implementation for byte strings.
    """
    # BSON document structure for binary data
    # Document length (4 bytes) + type + key + null + binary data
    binary_data = bytes([0x00]) + struct.pack("<I", len(data)) + bytes([0x00]) + data
    doc_length = 4 + 1 + len(b"") + 1 + len(binary_data) + 1  # key is empty for simplicity
    
    # Full BSON document
    result = struct.pack("<I", doc_length)
    result += bytes([0x00])  # Binary type
    result += b"\x00"  # Empty key (null-terminated)
    result += binary_data
    result += bytes([0x00])  # Document terminator
    
    return result


def bson_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode BSON binary data.
    """
    if len(data) < 5:
        raise ValueError("Invalid BSON data")
    
    # Read document length
    doc_length = struct.unpack("<I", data[0:4])[0]
    
    # Skip to binary data type
    offset = 4
    if data[offset] == 0x00:  # Binary type
        offset += 1
        # Skip key (null-terminated)
        while offset < len(data) and data[offset] != 0x00:
            offset += 1
        offset += 1  # Skip null terminator
        
        # Read binary length
        if offset + 4 <= len(data):
            bin_length = struct.unpack("<I", data[offset:offset+4])[0]
            offset += 4
            # Skip subtype byte
            offset += 1
            return data[offset:offset+bin_length]
    
    raise ValueError("Could not find binary data in BSON")


# =============================================================================
# PROTOBUF-STYLE ENCODING (Varint + length-prefixed)
# =============================================================================
def protobuf_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data in Protobuf-like varint length-prefixed format.
    Simplified implementation.
    """
    def encode_varint(value: int) -> bytes:
        result = bytearray()
        while value > 0x7F:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)
    
    # Field tag (field 1, wire type 2 = length-delimited)
    tag = bytes([0x0A])
    length = encode_varint(len(data))
    return tag + length + data


def protobuf_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode Protobuf varint length-prefixed format.
    """
    def decode_varint(data: bytes, offset: int) -> tuple[int, int]:
        result = 0
        shift = 0
        while offset < len(data):
            byte = data[offset]
            result |= (byte & 0x7F) << shift
            offset += 1
            if not (byte & 0x80):
                break
            shift += 7
        return result, offset
    
    offset = 0
    if offset < len(data) and data[offset] == 0x0A:
        offset += 1
    
    length, offset = decode_varint(data, offset)
    return data[offset:offset+length]


# =============================================================================
# AVRO ENCODING (Simplified)
# =============================================================================
def avro_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data in Avro binary format (simplified).
    Uses length-prefixed bytes format.
    """
    # Avro bytes encoding: length (varint) + data
    def encode_varint(value: int) -> bytes:
        result = bytearray()
        # Zigzag encoding for signed, but we use unsigned
        while value > 0x7F:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)
    
    return encode_varint(len(data)) + data


def avro_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode Avro binary format.
    """
    def decode_varint(data: bytes, offset: int) -> tuple[int, int]:
        result = 0
        shift = 0
        while offset < len(data):
            byte = data[offset]
            result |= (byte & 0x7F) << shift
            offset += 1
            if not (byte & 0x80):
                break
            shift += 7
        return result, offset
    
    length, offset = decode_varint(data, 0)
    return data[offset:offset+length]


# =============================================================================
# PICKLE-LIKE ENCODING (Python-safe binary)
# =============================================================================
def pickle_safe_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data in a pickle-like safe binary format.
    Not actual pickle (for security), but similar structure.
    """
    # Format: MAGIC + version + length + data + checksum
    MAGIC = b"OMNI"
    VERSION = b"\x01"
    
    import zlib
    checksum = zlib.crc32(data) & 0xFFFFFFFF
    
    result = MAGIC + VERSION
    result += struct.pack("<I", len(data))
    result += data
    result += struct.pack("<I", checksum)
    
    return result


def pickle_safe_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode pickle-safe format.
    """
    import zlib
    
    if len(data) < 13:  # MAGIC(4) + VERSION(1) + LENGTH(4) + CHECKSUM(4)
        raise ValueError("Invalid pickle-safe data")
    
    if data[:4] != b"OMNI":
        raise ValueError("Invalid magic bytes")
    
    offset = 5  # Skip magic and version
    length = struct.unpack("<I", data[offset:offset+4])[0]
    offset += 4
    
    payload = data[offset:offset+length]
    offset += length
    
    stored_checksum = struct.unpack("<I", data[offset:offset+4])[0]
    calculated_checksum = zlib.crc32(payload) & 0xFFFFFFFF
    
    if stored_checksum != calculated_checksum:
        raise ValueError("Checksum mismatch")
    
    return payload


# =============================================================================
# TOML ADVANCED ENCODING
# =============================================================================
def toml_advanced_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data as TOML with metadata.
    """
    import time
    from datetime import datetime
    
    text = _to_text(data, options)
    escaped = text.replace("\n", "\\n").replace('"', '\\"').replace("\\", "\\\\")
    
    timestamp = datetime.now().isoformat()
    
    toml_content = f'''[data]
content = "{escaped}"
encoding = "utf-8"
timestamp = "{timestamp}"
size = {len(data)}
'''
    return toml_content.encode("utf-8")


def toml_advanced_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode TOML and extract content.
    """
    text = _to_text(data, options)
    
    # Simple TOML parser for our format
    import re
    
    match = re.search(r'content\s*=\s*"((?:[^"\\]|\\.)*)"', text)
    if match:
        content = match.group(1)
        # Unescape
        content = content.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
        return content.encode("utf-8")
    
    return text.encode("utf-8")


# =============================================================================
# JSON5 ENCODING (JSON with comments and trailing commas)
# =============================================================================
def json5_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data as JSON5 (JSON with additional features).
    """
    text = _to_text(data, options)
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    
    json5_content = f'''{{
  // OMNICODEC JSON5 encoded data
  "data": "{escaped}",
  "encoding": "utf-8",
}}
'''
    return json5_content.encode("utf-8")


def json5_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode JSON5 and extract data.
    """
    text = _to_text(data, options)
    
    # Remove comments
    import re
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    
    # Parse JSON
    match = re.search(r'"data"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
    if match:
        content = match.group(1)
        content = content.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
        return content.encode("utf-8")
    
    return text.encode("utf-8")


def get_specs() -> list[MethodSpec]:
    return [
        # YAML
        MethodSpec("yaml", "serialization_advanced", "YAML serialization", yaml_encode, yaml_decode),
        
        # Binary serialization
        MethodSpec("msgpack", "serialization_advanced", "MessagePack binary format", msgpack_encode, msgpack_decode, aliases=("msg",)),
        MethodSpec("cbor", "serialization_advanced", "CBOR (RFC 7049)", cbor_encode, cbor_decode),
        MethodSpec("bson", "serialization_advanced", "BSON binary JSON", bson_encode, bson_decode),
        
        # Protocol buffers style
        MethodSpec("protobuf", "serialization_advanced", "Protobuf-style varint encoding", protobuf_encode, protobuf_decode, aliases=("proto",)),
        MethodSpec("avro", "serialization_advanced", "Avro binary format", avro_encode, avro_decode),
        
        # Python-safe
        MethodSpec("pickle_safe", "serialization_advanced", "Pickle-like safe binary", pickle_safe_encode, pickle_safe_decode),
        
        # Enhanced formats
        MethodSpec("toml_advanced", "serialization_advanced", "TOML with metadata", toml_advanced_encode, toml_advanced_decode),
        MethodSpec("json5", "serialization_advanced", "JSON5 (extended JSON)", json5_encode, json5_decode),
    ]
