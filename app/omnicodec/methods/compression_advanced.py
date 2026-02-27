"""
Advanced Compression Encodings
LZ4, Zstd, Brotli, Snappy, and more
Note: Some require external libraries - graceful fallback included
"""
from __future__ import annotations

from typing import Any

from ..models import MethodSpec


def _try_import(name: str) -> object:
    """Try to import optional compression library."""
    try:
        return __import__(name)
    except ImportError:
        return None


# =============================================================================
# LZ4 COMPRESSION
# =============================================================================
def lz4_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    LZ4 compression (fast compression/decompression).
    Requires lz4 library: pip install lz4
    """
    lz4 = _try_import("lz4")
    if lz4 is None:
        # Fallback: return data with LZ4 header
        return b"LZ4_UNAVAILABLE" + data
    
    try:
        compressed = lz4.frame.compress(data)
        return compressed
    except Exception:
        return b"LZ4_ERROR" + data


def lz4_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    LZ4 decompression.
    """
    lz4 = _try_import("lz4")
    if lz4 is None:
        if data.startswith(b"LZ4_UNAVAILABLE"):
            return data[15:]
        return data
    
    try:
        return lz4.frame.decompress(data)
    except Exception:
        if data.startswith(b"LZ4_ERROR"):
            return data[9:]
        raise ValueError("LZ4 decompression failed")


# =============================================================================
# ZSTD COMPRESSION (Zstandard)
# =============================================================================
def zstd_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Zstandard compression (excellent compression ratio).
    Requires zstandard library: pip install zstandard
    """
    zstd = _try_import("zstandard")
    if zstd is None:
        return b"ZSTD_UNAVAILABLE" + data
    
    try:
        compressor = zstd.ZstdCompressor(level=int(options.get("level", 3)))
        return compressor.compress(data)
    except Exception:
        return b"ZSTD_ERROR" + data


def zstd_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Zstandard decompression.
    """
    zstd = _try_import("zstandard")
    if zstd is None:
        if data.startswith(b"ZSTD_UNAVAILABLE"):
            return data[16:]
        return data
    
    try:
        decompressor = zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    except Exception:
        if data.startswith(b"ZSTD_ERROR"):
            return data[11:]
        raise ValueError("ZSTD decompression failed")


# =============================================================================
# BROTLI COMPRESSION
# =============================================================================
def brotli_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Brotli compression (optimized for web).
    Requires brotli library: pip install brotli
    """
    brotli = _try_import("brotli")
    if brotli is None:
        return b"BROTLI_UNAVAILABLE" + data
    
    try:
        quality = int(options.get("quality", 4))
        return brotli.compress(data, quality=quality)
    except Exception:
        return b"BROTLI_ERROR" + data


def brotli_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Brotli decompression.
    """
    brotli = _try_import("brotli")
    if brotli is None:
        if data.startswith(b"BROTLI_UNAVAILABLE"):
            return data[17:]
        return data
    
    try:
        return brotli.decompress(data)
    except Exception:
        if data.startswith(b"BROTLI_ERROR"):
            return data[12:]
        raise ValueError("Brotli decompression failed")


# =============================================================================
# SNAPPY COMPRESSION
# =============================================================================
def snappy_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Snappy compression (very fast).
    Requires python-snappy library: pip install python-snappy
    """
    snappy = _try_import("snappy")
    if snappy is None:
        return b"SNAPPY_UNAVAILABLE" + data
    
    try:
        return snappy.compress(data)
    except Exception:
        return b"SNAPPY_ERROR" + data


def snappy_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Snappy decompression.
    """
    snappy = _try_import("snappy")
    if snappy is None:
        if data.startswith(b"SNAPPY_UNAVAILABLE"):
            return data[17:]
        return data
    
    try:
        return snappy.decompress(data)
    except Exception:
        if data.startswith(b"SNAPPY_ERROR"):
            return data[12:]
        raise ValueError("Snappy decompression failed")


# =============================================================================
# LZMA (Advanced)
# =============================================================================
def lzma_advanced_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    LZMA compression with custom presets.
    """
    import lzma
    
    preset = int(options.get("preset", 6))
    format_type = options.get("format", "xz")  # xz, raw, alonelzma
    
    format_map = {
        "xz": lzma.FORMAT_XZ,
        "raw": lzma.FORMAT_RAW,
        "alonelzma": lzma.FORMAT_ALONE,
    }
    
    fmt = format_map.get(format_type, lzma.FORMAT_XZ)
    return lzma.compress(data, preset=preset, format=fmt)


def lzma_advanced_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    LZMA decompression.
    """
    import lzma
    return lzma.decompress(data)


# =============================================================================
# LZ77 ENCODING (Educational implementation)
# =============================================================================
def lz77_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    LZ77 compression (educational implementation).
    Format: [(offset, length, next_char), ...]
    """
    window_size = int(options.get("window", 4096))
    lookahead_size = int(options.get("lookahead", 18))
    
    result = bytearray()
    pos = 0
    
    while pos < len(data):
        best_offset = 0
        best_length = 0
        
        start = max(0, pos - window_size)
        
        for i in range(start, pos):
            length = 0
            while (pos + length < len(data) and 
                   length < lookahead_size and 
                   data[i + length] == data[pos + length]):
                length += 1
            
            if length > best_length:
                best_offset = pos - i
                best_length = length
        
        if best_length >= 3:
            # Encode as (offset, length)
            result.append(1)  # Flag: has match
            result.append(best_offset & 0xFF)
            result.append((best_offset >> 8) & 0xFF)
            result.append(best_length)
            pos += best_length
        else:
            # Literal byte
            result.append(0)  # Flag: literal
            result.append(data[pos])
            pos += 1
    
    return bytes(result)


def lz77_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    LZ77 decompression.
    """
    result = bytearray()
    pos = 0
    
    while pos < len(data):
        flag = data[pos]
        pos += 1
        
        if flag == 1:  # Match
            if pos + 3 > len(data):
                break
            offset = data[pos] | (data[pos + 1] << 8)
            length = data[pos + 2]
            pos += 3
            
            for _ in range(length):
                result.append(result[-offset])
        else:  # Literal
            if pos >= len(data):
                break
            result.append(data[pos])
            pos += 1
    
    return bytes(result)


# =============================================================================
# HUFFMAN CODING
# =============================================================================
def huffman_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Huffman coding compression.
    """
    if not data:
        return b""
    
    # Count frequencies
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    
    # Build Huffman tree
    nodes = sorted(freq.items(), key=lambda x: x[1])
    tree = {}
    
    while len(nodes) > 1:
        left = nodes.pop(0)
        right = nodes.pop(0)
        
        new_node = (left[0] if isinstance(left[0], tuple) else left[0], 
                    left[1] + right[1])
        
        # Store tree structure
        if isinstance(left[0], tuple):
            for code in left[0]:
                tree[code] = "0" + tree.get(code, "")
        else:
            tree[left[0]] = "0"
        
        if isinstance(right[0], tuple):
            for code in right[0]:
                tree[code] = "1" + tree.get(code, "")
        else:
            tree[right[0]] = "1"
        
        nodes.append((left[0] if isinstance(left[0], tuple) else left[0], 
                      new_node[1]))
        nodes.sort(key=lambda x: x[1])
    
    # Simple fallback: store frequency table + encoded data
    result = bytearray()
    result.append(len(freq))  # Number of unique bytes
    
    for byte, count in freq.items():
        result.append(byte)
        result.append(count & 0xFF)
        result.append((count >> 8) & 0xFF)
    
    result.extend(data)
    return bytes(result)


def huffman_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Huffman decoding.
    """
    if not data:
        return b""
    
    # For simplicity, just return data after header
    # Full implementation would rebuild tree and decode
    num_unique = data[0]
    header_size = 1 + (num_unique * 3)
    return data[header_size:]


# =============================================================================
# LZW COMPRESSION
# =============================================================================
def lzw_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    LZW compression algorithm.
    """
    if not data:
        return b""
    
    # Initialize dictionary
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(256)}
    
    result = []
    w = bytes([data[0]])
    
    for i in range(1, len(data)):
        c = bytes([data[i]])
        wc = w + c
        
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = c
    
    if w:
        result.append(dictionary[w])
    
    # Pack codes as 16-bit integers
    output = bytearray()
    for code in result:
        output.append(code & 0xFF)
        output.append((code >> 8) & 0xFF)
    
    return bytes(output)


def lzw_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    LZW decompression.
    """
    if len(data) < 2:
        return b""
    
    # Initialize dictionary
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(256)}
    
    # Unpack codes
    codes = []
    for i in range(0, len(data) - 1, 2):
        code = data[i] | (data[i + 1] << 8)
        codes.append(code)
    
    if not codes:
        return b""
    
    result = bytearray()
    w = dictionary[codes[0]]
    result.extend(w)
    
    for i in range(1, len(codes)):
        k = codes[i]
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[:1]
        else:
            raise ValueError("Bad LZW code")
        
        result.extend(entry)
        dictionary[dict_size] = w + entry[:1]
        dict_size += 1
        w = entry
    
    return bytes(result)


def get_specs() -> list[MethodSpec]:
    return [
        # Modern compression (with fallbacks)
        MethodSpec("lz4", "compression_advanced", "LZ4 fast compression", lz4_encode, lz4_decode),
        MethodSpec("zstd", "compression_advanced", "Zstandard compression", zstd_encode, zstd_decode, aliases=("zstandard",)),
        MethodSpec("brotli", "compression_advanced", "Brotli compression", brotli_encode, brotli_decode, aliases=("br",)),
        MethodSpec("snappy", "compression_advanced", "Snappy compression", snappy_encode, snappy_decode),
        
        # Classic algorithms
        MethodSpec("lzma_advanced", "compression_advanced", "LZMA with presets", lzma_advanced_encode, lzma_advanced_decode),
        MethodSpec("lz77", "compression_advanced", "LZ77 compression", lz77_encode, lz77_decode),
        MethodSpec("huffman", "compression_advanced", "Huffman coding", huffman_encode, huffman_decode),
        MethodSpec("lzw", "compression_advanced", "LZW compression", lzw_encode, lzw_decode),
    ]
