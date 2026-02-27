"""
Esoteric & Abnormal Encodings
Brainfuck, Zalgo, Emoji, Kaomoji, Whitespace, Ook, and other unusual encodings
"""
from __future__ import annotations

import random
from typing import Any

from ..models import MethodSpec


# =============================================================================
# BRAINFUCK ENCODING
# =============================================================================

def _to_text(data: bytes, options: dict[str, Any]) -> str:
    return data.decode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


def _to_bytes(text: str, options: dict[str, Any]) -> bytes:
    return text.encode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


# -----------------------------------------------------------------------------
# Brainfuck Encoding - Encode data as Brainfuck code
# -----------------------------------------------------------------------------
def brainfuck_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes as Brainfuck code.
    Uses a simple approach: output each byte value using + and . commands.
    """
    result = []
    use_loops = options.get("loops", False)
    
    if use_loops:
        # More advanced: use loops for repeated patterns
        prev = 0
        for byte in data:
            diff = byte - prev
            if diff > 0:
                result.append("+" * diff)
            elif diff < 0:
                result.append("-" * (-diff))
            result.append(".")
            prev = byte
    else:
        # Simple: just output the byte value directly
        for byte in data:
            result.append("+" * byte + ".")
    
    return "".join(result).encode("utf-8")


def brainfuck_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode Brainfuck code by interpreting it.
    Note: This is a simplified interpreter - only handles basic operations.
    """
    code = _to_text(data, options)
    
    # Simple BF interpreter (only +, -, . commands for decoding)
    cell = 0
    output = bytearray()
    
    for ch in code:
        if ch == "+":
            cell = (cell + 1) % 256
        elif ch == "-":
            cell = (cell - 1) % 256
        elif ch == ".":
            output.append(cell)
        # Ignore other BF commands for simplicity
    
    return bytes(output)


# -----------------------------------------------------------------------------
# Whitespace Encoding - Encode using only whitespace characters
# -----------------------------------------------------------------------------
# W = Space ( ), T = Tab (\t), N = Newline (\n)
WS_MAP = {
    "00": " ",   # Space
    "01": "\t",  # Tab
    "10": "\n",  # Newline
}

WS_REV = {" ": "00", "\t": "01", "\n": "10"}


def whitespace_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes using only whitespace characters (Space, Tab, Newline).
    Each byte is represented as 8 bits using 3 whitespace characters.
    """
    result = []
    for byte in data:
        # Convert byte to 6-bit binary (pad with leading zeros)
        binary = format(byte, "08b")
        # Split into pairs and map to whitespace
        for i in range(0, 8, 2):
            pair = binary[i:i+2]
            result.append(WS_MAP[pair])
    return "".join(result).encode("utf-8")


def whitespace_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode whitespace-only encoding back to bytes."""
    text = _to_text(data, options)
    result = []
    
    # Collect whitespace characters
    bits = ""
    for ch in text:
        if ch in WS_REV:
            bits += WS_REV[ch]
            if len(bits) == 8:
                result.append(int(bits, 2))
                bits = ""
    
    return bytes(result)


# -----------------------------------------------------------------------------
# Ook Encoding - Based on Orangutan language (Brainfuck variant)
# -----------------------------------------------------------------------------
OOK_PAIRS = {
    "++": "Ook. Ook?",
    "+-": "Ook. Ook!",
    "+!": "Ook? Ook.",
    "-+": "Ook? Ook!",
    "-!": "Ook! Ook.",
    "!+": "Ook! Ook?",
    "!!": "Ook. Ook.",
    "!-": "Ook? Ook?",
}

OOK_REV = {v: k for k, v in OOK_PAIRS.items()}


def ook_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes using Ook! language (Brainfuck variant for orangutans).
    """
    result = []
    for byte in data:
        # Convert to 6-bit representation using Ook pairs
        binary = format(byte, "06b")
        for i in range(0, 6, 2):
            pair = binary[i:i+2]
            result.append(OOK_PAIRS.get(pair, "Ook. Ook."))
    return " ".join(result).encode("utf-8")


def ook_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode Ook! language back to bytes."""
    text = _to_text(data, options)
    # Split by spaces and process pairs
    words = text.split()
    result = []
    
    i = 0
    while i < len(words) - 1:
        pair = f"{words[i]} {words[i+1]}"
        if pair in OOK_REV:
            binary = OOK_REV[pair]
            # Collect 3 pairs to make 6 bits
            if len(result) % 3 == 0:
                result.append([binary])
            else:
                result[-1].append(binary)
        i += 2
    
    # Convert to bytes
    output = []
    for group in result:
        if len(group) == 3:
            binary = "".join(group)
            output.append(int(binary, 2))
    
    return bytes(output)


# -----------------------------------------------------------------------------
# Zalgo Text Encoding - Add combining diacritical marks
# -----------------------------------------------------------------------------
# Unicode combining diacritical marks
ZALGO_MARKS = [
    "\u0300", "\u0301", "\u0302", "\u0303", "\u0304", "\u0305", "\u0306", "\u0307",
    "\u0308", "\u0309", "\u030A", "\u030B", "\u030C", "\u030D", "\u030E", "\u030F",
    "\u0310", "\u0311", "\u0312", "\u0313", "\u0314", "\u0315", "\u0316", "\u0317",
    "\u0318", "\u0319", "\u031A", "\u031B", "\u031C", "\u031D", "\u031E", "\u031F",
    "\u0320", "\u0321", "\u0322", "\u0323", "\u0324", "\u0325", "\u0326", "\u0327",
    "\u0328", "\u0329", "\u032A", "\u032B", "\u032C", "\u032D", "\u032E", "\u032F",
    "\u0330", "\u0331", "\u0332", "\u0333", "\u0334", "\u0335", "\u0336", "\u0337",
    "\u0338", "\u0339", "\u033A", "\u033B", "\u033C", "\u033D", "\u033E", "\u033F",
]


def zalgo_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode text with Zalgo corruption (combining diacritical marks).
    This is a stylistic encoding that makes text look "corrupted".
    """
    text = _to_text(data, options)
    intensity = int(options.get("intensity", 3))  # Number of marks per character
    
    result = []
    for ch in text:
        result.append(ch)
        # Add random combining marks
        num_marks = random.randint(1, intensity)
        marks = random.sample(ZALGO_MARKS, num_marks)
        result.extend(marks)
    
    return "".join(result).encode("utf-8")


def zalgo_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode Zalgo text by removing combining diacritical marks.
    """
    text = _to_text(data, options)
    # Filter out combining diacritical marks (U+0300 - U+036F)
    result = []
    for ch in text:
        code = ord(ch)
        if not (0x0300 <= code <= 0x036F):
            result.append(ch)
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Kaomoji Encoding - Encode as Japanese emoticons
# -----------------------------------------------------------------------------
KAOMOJI_MAP = {
    "a": "(^ω^)", "b": "(¬_¬)", "c": "(>_<)", "d": "(O_O)",
    "e": "(+_+)", "f": "(-_-)", "g": "(T_T)", "h": "(^_^)",
    "i": "(o_o)", "j": "(X_X)", "k": "(U_U)", "l": "(O_O)",
    "m": "(>_<)", "n": "(¬_¬)", "o": "(^o^)", "p": "(^_^)",
    "q": "(Q_Q)", "r": "(R_R)", "s": "(S_S)", "t": "(T_T)",
    "u": "(U_U)", "v": "(V_V)", "w": "(W_W)", "x": "(X_X)",
    "y": "(Y_Y)", "z": "(Z_Z)",
    "A": "【^o^】", "B": "【^_^】", "C": "【>_<】", "D": "【O_O】",
    "E": "【+_+】", "F": "【-_-】", "G": "【T_T】", "H": "【^_^】",
    "0": "(0_0)", "1": "(1_1)", "2": "(2_2)", "3": "(3_3)",
    "4": "(4_4)", "5": "(5_5)", "6": "(6_6)", "7": "(7_7)",
    "8": "(8_8)", "9": "(9_9)",
    " ": "   ", ".": "(._.)", ",": "(,_)", "!": "(>_<)", "?": "(?_?)",
}


def kaomoji_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode ASCII text as Kaomoji (Japanese emoticons).
    Each character is mapped to a corresponding emoticon.
    """
    text = _to_text(data, options).lower()
    result = []
    for ch in text:
        result.append(KAOMOJI_MAP.get(ch, f"({ch})"))
    return "".join(result).encode("utf-8")


def kaomoji_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode Kaomoji back to ASCII (approximate).
    This is a best-effort decode since kaomoji encoding is lossy.
    """
    text = _to_text(data, options)
    result = []
    
    # Simple approach: extract characters from parentheses
    i = 0
    while i < len(text):
        if text[i] == "(":
            # Find closing paren
            end = text.find(")", i)
            if end != -1:
                content = text[i+1:end]
                # Try to extract original character
                if len(content) == 3 and content[1] == "_":
                    result.append(content[0])
                elif len(content) == 1:
                    result.append(content)
                else:
                    result.append("?")
                i = end + 1
            else:
                i += 1
        elif text[i] == "[":
            end = text.find("]", i)
            if end != -1:
                content = text[i+1:end]
                if len(content) >= 3:
                    result.append(content[1])
                i = end + 1
            else:
                i += 1
        else:
            i += 1
    
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Emoji Encoding - Encode bytes as emoji sequences
# -----------------------------------------------------------------------------
# Use a set of common emojis for encoding
EMOJI_SET = [
    "😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆",
    "😉", "😊", "😋", "😎", "😍", "😘", "🥰", "😗",
    "😙", "😚", "🙂", "🤗", "🤩", "🤔", "🤨", "😐",
    "😑", "😶", "🙄", "😏", "😣", "😥", "😮", "🤐",
    "😯", "😪", "😫", "😴", "😌", "😛", "😜", "😝",
    "🤤", "😒", "😓", "😔", "😕", "🙃", "🤑", "😲",
    "☹️", "🙁", "😖", "😞", "😟", "😤", "😢", "😭",
    "😦", "😧", "😨", "😩", "🤯", "😬", "😰", "😱",
]


def emoji_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode bytes as emoji sequences.
    Each byte value (0-255) maps to a combination of emojis.
    """
    result = []
    for byte in data:
        # Use two emojis to represent each byte (16*16 = 256 combinations)
        high = byte // 16
        low = byte % 16
        result.append(EMOJI_SET[high])
        result.append(EMOJI_SET[low])
    return "".join(result).encode("utf-8")


def emoji_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode emoji sequences back to bytes."""
    text = _to_text(data, options)
    result = []
    
    # Filter to only our emoji set
    emojis = [ch for ch in text if ch in EMOJI_SET or any(ch in s for s in EMOJI_SET)]
    
    # Process pairs
    i = 0
    while i < len(emojis) - 1:
        # Find indices
        high_idx = None
        low_idx = None
        
        for idx, emoji in enumerate(EMOJI_SET):
            if emojis[i] in emoji or emoji in emojis[i]:
                high_idx = idx
                break
        
        for idx, emoji in enumerate(EMOJI_SET):
            if emojis[i+1] in emoji or emoji in emojis[i+1]:
                low_idx = idx
                break
        
        if high_idx is not None and low_idx is not None:
            byte = (high_idx * 16) + low_idx
            result.append(byte)
        
        i += 2
    
    return bytes(result)


# -----------------------------------------------------------------------------
# Reverse Text Encoding
# -----------------------------------------------------------------------------
def reverse_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Reverse the byte sequence."""
    return data[::-1]


def reverse_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Reverse back to original."""
    return data[::-1]


# -----------------------------------------------------------------------------
# Mirror/Flip Text
# -----------------------------------------------------------------------------
MIRROR_MAP = str.maketrans({
    "a": "ɒ", "b": "q", "c": "ɔ", "d": "p", "e": "ɘ", "f": "Ꮈ",
    "g": "ǫ", "h": "ʜ", "i": "i", "j": "ꞁ", "k": "ʞ", "l": "l",
    "m": "m", "n": "u", "o": "o", "p": "d", "q": "b", "r": "ɿ",
    "s": "ꙅ", "t": "ƚ", "u": "n", "v": "v", "w": "w", "x": "x",
    "y": "y", "z": "z",
    "A": "∀", "B": "𐐒", "C": "Ɔ", "D": "ᗡ", "E": "Ǝ", "F": "ꟻ",
    "G": "Ꭾ", "H": "H", "I": "I", "J": "Ⴑ", "K": "⋊", "L": "⅃",
    "M": "M", "N": "И", "O": "O", "P": "Ԁ", "Q": "Ό", "R": "Я",
    "S": "S", "T": "┴", "U": "∩", "V": "Λ", "W": "W", "X": "X",
    "Y": "⅄", "Z": "Z",
    "0": "0", "1": "Ɩ", "2": "ᄅ", "3": "Ɛ", "4": "h", "5": "S",
    "6": "9", "7": "L", "8": "8", "9": "6",
    ".": "˙", ",": "'", "'": ",", "!": "¡", "?": "¿",
    "(": ")", ")": "(", "[": "]", "]": "[",
    "<": ">", ">": "<", "&": "⅋", "_": "‾",
})

MIRROR_REV = {v: k for k, v in MIRROR_MAP.items()}


def mirror_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Mirror/flip text upside down and backwards."""
    text = _to_text(data, options)
    # Reverse and translate
    mirrored = text[::-1].translate(MIRROR_MAP)
    return mirrored.encode("utf-8")


def mirror_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Unmirror text."""
    text = _to_text(data, options)
    # Reverse and translate back
    unmirrored = text[::-1].translate(MIRROR_REV)
    return unmirrored.encode("utf-8")


# -----------------------------------------------------------------------------
# Small Caps Encoding
# -----------------------------------------------------------------------------
SMALL_CAPS_MAP = str.maketrans({
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ",
    "g": "ɢ", "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ",
    "m": "ᴍ", "n": "ɴ", "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ",
    "s": "s", "t": "ᴛ", "u": "ᴜ", "v": "ᴠ", "w": "ᴡ", "x": "x",
    "y": "ʏ", "z": "ᴢ",
})


def small_caps_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert lowercase text to small caps."""
    text = _to_text(data, options)
    return text.translate(SMALL_CAPS_MAP).encode("utf-8")


def small_caps_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert small caps back to lowercase."""
    text = _to_text(data, options)
    rev_map = {v: k for k, v in SMALL_CAPS_MAP.items()}
    return text.translate(str.maketrans(rev_map)).encode("utf-8")


# -----------------------------------------------------------------------------
# Circled Text Encoding
# -----------------------------------------------------------------------------
CIRCLED_MAP = {}
# Build circled character mapping
for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    CIRCLED_MAP[ch] = chr(0x24B6 + i)  # Circled capital letters
for i, ch in enumerate("abcdefghijklmnopqrstuvwxyz"):
    CIRCLED_MAP[ch] = chr(0x24D0 + i)  # Circled small letters
for i, ch in enumerate("0123456789"):
    CIRCLED_MAP[ch] = chr(0x2460 + i)  # Circled numbers


def circled_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert text to circled Unicode characters."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        result.append(CIRCLED_MAP.get(ch, ch))
    return "".join(result).encode("utf-8")


def circled_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert circled text back to ASCII."""
    text = _to_text(data, options)
    rev_map = {v: k for k, v in CIRCLED_MAP.items()}
    result = []
    for ch in text:
        result.append(rev_map.get(ch, ch))
    return "".join(result).encode("utf-8")


# -----------------------------------------------------------------------------
# Double-Struck (Blackboard Bold) Encoding
# -----------------------------------------------------------------------------
DOUBLE_STRUCK_MAP = {}
for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    DOUBLE_STRUCK_MAP[ch] = chr(0x1D538 + i)
for i, ch in enumerate("abcdefghijklmnopqrstuvwxyz"):
    DOUBLE_STRUCK_MAP[ch] = chr(0x1D552 + i)
for i, ch in enumerate("0123456789"):
    DOUBLE_STRUCK_MAP[ch] = chr(0x1D7D8 + i)


def double_struck_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert text to double-struck (blackboard bold) Unicode."""
    text = _to_text(data, options)
    result = []
    for ch in text:
        result.append(DOUBLE_STRUCK_MAP.get(ch, ch))
    return "".join(result).encode("utf-8")


def double_struck_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Convert double-struck text back to ASCII."""
    text = _to_text(data, options)
    rev_map = {v: k for k, v in DOUBLE_STRUCK_MAP.items()}
    result = []
    for ch in text:
        result.append(rev_map.get(ch, ch))
    return "".join(result).encode("utf-8")


def get_specs() -> list[MethodSpec]:
    return [
        # Esoteric programming languages
        MethodSpec("brainfuck", "esoteric_abnormal", "Brainfuck esoteric language", brainfuck_encode, brainfuck_decode, aliases=("bf",)),
        MethodSpec("whitespace", "esoteric_abnormal", "Whitespace-only encoding", whitespace_encode, whitespace_decode, aliases=("ws",)),
        MethodSpec("ook", "esoteric_abnormal", "Ook! orangutan language", ook_encode, ook_decode),
        
        # Abnormal/stylistic
        MethodSpec("zalgo", "esoteric_abnormal", "Zalgo corrupted text", zalgo_encode, zalgo_decode, aliases=("corrupt",)),
        MethodSpec("kaomoji", "esoteric_abnormal", "Japanese emoticon encoding", kaomoji_encode, kaomoji_decode, aliases=("emoticon",)),
        MethodSpec("emoji", "esoteric_abnormal", "Emoji sequence encoding", emoji_encode, emoji_decode),
        
        # Text transformations
        MethodSpec("reverse", "esoteric_abnormal", "Reverse byte sequence", reverse_encode, reverse_decode),
        MethodSpec("mirror", "esoteric_abnormal", "Mirror/flip text", mirror_encode, mirror_decode, aliases=("flip", "upsidedown")),
        MethodSpec("small_caps", "esoteric_abnormal", "Small caps text", small_caps_encode, small_caps_decode),
        MethodSpec("circled", "esoteric_abnormal", "Circled Unicode characters", circled_encode, circled_decode),
        MethodSpec("double_struck", "esoteric_abnormal", "Double-struck (blackboard bold)", double_struck_encode, double_struck_decode, aliases=("blackboard",)),
    ]
