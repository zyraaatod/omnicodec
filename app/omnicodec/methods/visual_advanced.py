"""
Visual & Signal Encodings
Braille, NATO phonetic, Color codes, QR payload, and more
"""
from __future__ import annotations

from typing import Any

from ..models import MethodSpec


def _to_text(data: bytes, options: dict[str, Any]) -> str:
    return data.decode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


def _to_bytes(text: str, options: dict[str, Any]) -> bytes:
    return text.encode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


# =============================================================================
# BRAILLE ENCODING
# =============================================================================
# Braille Unicode: U+2800 to U+28FF
# Each braille character represents 8 bits (dots 1-8)
BRAILLE_BASE = 0x2800


def braille_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes as Braille Unicode characters.
    Each braille character encodes 8 bits (one byte).
    """
    result = []
    for byte in data:
        # Map each bit to a braille dot
        braille_code = BRAILLE_BASE
        if byte & 0x01:
            braille_code += 1  # Dot 1
        if byte & 0x02:
            braille_code += 2  # Dot 2
        if byte & 0x04:
            braille_code += 4  # Dot 3
        if byte & 0x08:
            braille_code += 8  # Dot 4
        if byte & 0x10:
            braille_code += 16  # Dot 5
        if byte & 0x20:
            braille_code += 32  # Dot 6
        if byte & 0x40:
            braille_code += 64  # Dot 7
        if byte & 0x80:
            braille_code += 128  # Dot 8
        result.append(chr(braille_code))
    return "".join(result).encode("utf-8")


def braille_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode Braille Unicode back to bytes.
    """
    text = _to_text(data, options)
    result = bytearray()
    
    for ch in text:
        code = ord(ch)
        if BRAILLE_BASE <= code < BRAILLE_BASE + 256:
            byte = 0
            offset = code - BRAILLE_BASE
            if offset & 1:
                byte |= 0x01
            if offset & 2:
                byte |= 0x02
            if offset & 4:
                byte |= 0x04
            if offset & 8:
                byte |= 0x08
            if offset & 16:
                byte |= 0x10
            if offset & 32:
                byte |= 0x20
            if offset & 64:
                byte |= 0x40
            if offset & 128:
                byte |= 0x80
            result.append(byte)
    
    return bytes(result)


# =============================================================================
# NATO PHONETIC ALPHABET
# =============================================================================
NATO_PHONETIC = {
    "A": "Alpha", "B": "Bravo", "C": "Charlie", "D": "Delta", "E": "Echo",
    "F": "Foxtrot", "G": "Golf", "H": "Hotel", "I": "India", "J": "Juliett",
    "K": "Kilo", "L": "Lima", "M": "Mike", "N": "November", "O": "Oscar",
    "P": "Papa", "Q": "Quebec", "R": "Romeo", "S": "Sierra", "T": "Tango",
    "U": "Uniform", "V": "Victor", "W": "Whiskey", "X": "X-ray", "Y": "Yankee",
    "Z": "Zulu",
    "0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four",
    "5": "Five", "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine",
}

NATO_REV = {v.lower(): k for k, v in NATO_PHONETIC.items()}


def nato_phonetic_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode text using NATO phonetic alphabet.
    """
    text = _to_text(data, options).upper()
    result = []
    for ch in text:
        if ch in NATO_PHONETIC:
            result.append(NATO_PHONETIC[ch])
        elif ch == " ":
            result.append("|")  # Word separator
        else:
            result.append(f"[{ch}]")
    return " ".join(result).encode("utf-8")


def nato_phonetic_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode NATO phonetic alphabet back to text.
    """
    text = _to_text(data, options)
    result = []
    
    words = text.split()
    for word in words:
        if word == "|":
            result.append(" ")
        elif word.startswith("[") and word.endswith("]"):
            result.append(word[1:-1])
        else:
            result.append(NATO_REV.get(word.lower(), "?"))
    
    return "".join(result).encode("utf-8")


# =============================================================================
# COLOR CODE ENCODING (RGB/HEX/HSL)
# =============================================================================
def rgb_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes as RGB color codes.
    Every 3 bytes become one RGB color.
    """
    result = []
    for i in range(0, len(data), 3):
        r = data[i]
        g = data[i + 1] if i + 1 < len(data) else 0
        b = data[i + 2] if i + 2 < len(data) else 0
        result.append(f"rgb({r},{g},{b})")
    return " ".join(result).encode("ascii")


def rgb_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode RGB color codes back to bytes.
    """
    import re
    text = _to_text(data, options)
    result = bytearray()
    
    for match in re.finditer(r"rgb\((\d+),(\d+),(\d+)\)", text):
        result.extend([int(match.group(1)), int(match.group(2)), int(match.group(3))])
    
    return bytes(result)


def hex_color_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes as hexadecimal color codes (#RRGGBB).
    """
    result = []
    for i in range(0, len(data), 3):
        r = data[i]
        g = data[i + 1] if i + 1 < len(data) else 0
        b = data[i + 2] if i + 2 < len(data) else 0
        result.append(f"#{r:02X}{g:02X}{b:02X}")
    return " ".join(result).encode("ascii")


def hex_color_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode hexadecimal color codes back to bytes.
    """
    import re
    text = _to_text(data, options)
    result = bytearray()
    
    for match in re.finditer(r"#([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})", text):
        result.extend([
            int(match.group(1), 16),
            int(match.group(2), 16),
            int(match.group(3), 16)
        ])
    
    return bytes(result)


def hsl_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes as HSL color codes.
    """
    result = []
    for i in range(0, len(data), 3):
        h = data[i]  # 0-255 -> 0-360
        s = data[i + 1] if i + 1 < len(data) else 0  # 0-100
        l = data[i + 2] if i + 2 < len(data) else 0  # 0-100
        h_deg = int(h * 360 / 255)
        result.append(f"hsl({h_deg},{s}%,{l}%)")
    return " ".join(result).encode("ascii")


def hsl_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode HSL color codes back to bytes.
    """
    import re
    text = _to_text(data, options)
    result = bytearray()
    
    for match in re.finditer(r"hsl\((\d+),(\d+)%,(\d+)%\)", text):
        h = int(match.group(1))
        s = int(match.group(2))
        l = int(match.group(3))
        result.extend([
            int(h * 255 / 360),
            min(s, 100),
            min(l, 100)
        ])
    
    return bytes(result)


# =============================================================================
# ANSI COLOR ENCODING
# =============================================================================
def ansi_color_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes with ANSI color codes.
    Each byte gets a different foreground color.
    """
    result = []
    for i, byte in enumerate(data):
        color_code = 30 + (i % 8)  # ANSI foreground colors 30-37
        result.append(f"\033[{color_code}m{chr(33 + (byte % 94))}")
    result.append("\033[0m")  # Reset
    return "".join(result).encode("ascii")


def ansi_color_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode ANSI color encoded text back to bytes.
    """
    import re
    text = _to_text(data, options)
    # Remove ANSI codes and extract characters
    clean = re.sub(r"\033\[\d+m", "", text)
    result = bytearray()
    for ch in clean:
        if 33 <= ord(ch) <= 126:
            result.append((ord(ch) - 33) % 256)
    return bytes(result)


# =============================================================================
# QR CODE PAYLOAD ENCODING
# =============================================================================
def qr_payload_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data as QR code payload format.
    Prepares data for QR code encoding.
    """
    # QR code uses specific encoding modes
    # This is a simplified representation
    mode = options.get("mode", "byte")  # numeric, alphanumeric, byte, kanji
    
    if mode == "byte":
        # Byte mode: 8-bit bytes
        return b"BYTE:" + data
    elif mode == "numeric":
        # Numeric mode: groups of 3 digits
        text = _to_text(data, options)
        return b"NUM:" + text.encode("ascii")
    else:
        return b"ALPHA:" + data


def qr_payload_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode QR code payload format.
    """
    text = _to_text(data, options)
    if text.startswith("BYTE:"):
        return text[5:].encode("utf-8")
    elif text.startswith("NUM:"):
        return text[4:].encode("utf-8")
    elif text.startswith("ALPHA:"):
        return text[6:].encode("utf-8")
    return data


# =============================================================================
# BINARY VISUAL ENCODING (With block characters)
# =============================================================================
def binary_visual_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes as visual binary using block characters.
    Uses ▓ for 1 and ░ for 0.
    """
    fill = options.get("fill", "blocks")  # blocks, dots, lines
    
    if fill == "blocks":
        one, zero = "▓", "░"
    elif fill == "dots":
        one, zero = "●", "○"
    elif fill == "lines":
        one, zero = "│", " "
    else:
        one, zero = "1", "0"
    
    result = []
    for byte in data:
        bits = format(byte, "08b")
        visual = "".join(one if b == "1" else zero for b in bits)
        result.append(visual)
    
    sep = options.get("separator", " ")
    return sep.join(result).encode("utf-8")


def binary_visual_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode visual binary back to bytes.
    """
    fill = options.get("fill", "blocks")
    
    if fill == "blocks":
        one, zero = "▓", "░"
    elif fill == "dots":
        one, zero = "●", "○"
    elif fill == "lines":
        one, zero = "│", " "
    else:
        one, zero = "1", "0"
    
    text = _to_text(data, options)
    sep = options.get("separator", " ")
    parts = text.split(sep) if sep else [text]
    
    result = bytearray()
    for part in parts:
        binary = part.replace(one, "1").replace(zero, "0").replace(" ", "")
        if len(binary) >= 8:
            result.append(int(binary[:8], 2))
    
    return bytes(result)


# =============================================================================
# WAVEFORM ENCODING (ASCII art representation)
# =============================================================================
def waveform_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes as ASCII waveform.
    """
    height = int(options.get("height", 8))
    chars = " ░▒▓█"
    
    result = []
    for byte in data:
        level = byte * (len(chars) - 1) // 255
        result.append(chars[level])
    
    return "".join(result).encode("utf-8")


def waveform_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode ASCII waveform back to bytes.
    """
    chars = " ░▒▓█"
    text = _to_text(data, options)
    
    result = bytearray()
    for ch in text:
        if ch in chars:
            level = chars.index(ch)
            byte = level * 255 // (len(chars) - 1)
            result.append(byte)
    
    return bytes(result)


# =============================================================================
# TACTILE/PHYSICAL ENCODING
# =============================================================================
def tap_code_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Tap code (prison code) encoding.
    Uses pairs of taps (1-5) to represent letters.
    """
    TAP_CODE = {
        "A": "(1,1)", "B": "(1,2)", "C": "(1,3)", "D": "(1,4)", "E": "(1,5)",
        "F": "(2,1)", "G": "(2,2)", "H": "(2,3)", "I": "(2,4)", "J": "(2,5)",
        "K": "(1,5)", "L": "(3,1)", "M": "(3,2)", "N": "(3,3)", "O": "(3,4)",
        "P": "(3,5)", "Q": "(4,1)", "R": "(4,2)", "S": "(4,3)", "T": "(4,4)",
        "U": "(4,5)", "V": "(5,1)", "W": "(5,2)", "X": "(5,3)", "Y": "(5,4)",
        "Z": "(5,5)",
        "1": "(6,1)", "2": "(6,2)", "3": "(6,3)", "4": "(6,4)", "5": "(6,5)",
        "6": "(7,1)", "7": "(7,2)", "8": "(7,3)", "9": "(7,4)", "0": "(7,5)",
    }
    
    text = _to_text(data, options).upper()
    result = []
    for ch in text:
        if ch in TAP_CODE:
            result.append(TAP_CODE[ch])
        elif ch == " ":
            result.append("/")
        else:
            result.append(f"[{ch}]")
    
    return " ".join(result).encode("ascii")


def tap_code_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode tap code back to text.
    """
    TAP_CODE_REV = {
        "(1,1)": "A", "(1,2)": "B", "(1,3)": "C", "(1,4)": "D", "(1,5)": "E",
        "(2,1)": "F", "(2,2)": "G", "(2,3)": "H", "(2,4)": "I", "(2,5)": "J",
        "(3,1)": "L", "(3,2)": "M", "(3,3)": "N", "(3,4)": "O", "(3,5)": "P",
        "(4,1)": "Q", "(4,2)": "R", "(4,3)": "S", "(4,4)": "T", "(4,5)": "U",
        "(5,1)": "V", "(5,2)": "W", "(5,3)": "X", "(5,4)": "Y", "(5,5)": "Z",
        "(6,1)": "1", "(6,2)": "2", "(6,3)": "3", "(6,4)": "4", "(6,5)": "5",
        "(7,1)": "6", "(7,2)": "7", "(7,3)": "8", "(7,4)": "9", "(7,5)": "0",
    }
    
    text = _to_text(data, options)
    result = []
    
    # Parse tap codes
    import re
    for match in re.finditer(r"\((\d+),(\d+)\)|([A-Z0-9])|/", text):
        if match.group(1):
            key = f"({match.group(1)},{match.group(2)})"
            result.append(TAP_CODE_REV.get(key, "?"))
        elif match.group(3):
            result.append(match.group(3))
        elif match.group(0) == "/":
            result.append(" ")
    
    return "".join(result).encode("utf-8")


def get_specs() -> list[MethodSpec]:
    return [
        # Tactile/Accessibility
        MethodSpec("braille", "visual_advanced", "Braille Unicode encoding", braille_encode, braille_decode),
        MethodSpec("tap_code", "visual_advanced", "Tap code (prison code)", tap_code_encode, tap_code_decode),
        
        # Phonetic
        MethodSpec("nato_phonetic", "visual_advanced", "NATO phonetic alphabet", nato_phonetic_encode, nato_phonetic_decode, aliases=("nato", "phonetic")),
        
        # Color encodings
        MethodSpec("rgb", "visual_advanced", "RGB color codes", rgb_encode, rgb_decode),
        MethodSpec("hex_color", "visual_advanced", "Hex color codes (#RRGGBB)", hex_color_encode, hex_color_decode, aliases=("hexcolor",)),
        MethodSpec("hsl", "visual_advanced", "HSL color codes", hsl_encode, hsl_decode),
        MethodSpec("ansi_color", "visual_advanced", "ANSI color terminal codes", ansi_color_encode, ansi_color_decode),
        
        # Visual representations
        MethodSpec("qr_payload", "visual_advanced", "QR code payload format", qr_payload_encode, qr_payload_decode),
        MethodSpec("binary_visual", "visual_advanced", "Visual binary with blocks", binary_visual_encode, binary_visual_decode),
        MethodSpec("waveform", "visual_advanced", "ASCII waveform", waveform_encode, waveform_decode),
    ]
