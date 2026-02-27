"""
Advanced Web & Network Encodings
CSS escape, JavaScript escape, JWT, URL parameters, and more
"""
from __future__ import annotations

import json
import re
import urllib.parse
from typing import Any

from ..models import MethodSpec


def _to_text(data: bytes, options: dict[str, Any]) -> str:
    return data.decode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


def _to_bytes(text: str, options: dict[str, Any]) -> bytes:
    return text.encode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


# =============================================================================
# CSS ESCAPE ENCODING
# =============================================================================
def css_escape_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Escape text for use in CSS strings and identifiers.
    Uses CSS Unicode escape sequences.
    """
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if code < 32 or code > 126:
            result.append(f"\\{code:X} ")
        elif ch == '"':
            result.append('\\"')
        elif ch == "'":
            result.append("\\'")
        elif ch == "\\":
            result.append("\\\\")
        elif ch == "{":
            result.append("\\{")
        elif ch == "}":
            result.append("\\}")
        elif ch == ":":
            result.append("\\:")
        elif ch == ";":
            result.append("\\;")
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def css_escape_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode CSS escaped text."""
    text = _to_text(data, options)
    
    def replace_escape(match):
        if match.group(1):  # Unicode escape \XXXX
            return chr(int(match.group(1), 16))
        elif match.group(0) == "\\\\":
            return "\\"
        else:
            return match.group(0)[1:]  # Remove backslash
    
    result = re.sub(r"\\([0-9A-Fa-f]+)\s*|\\(.)", replace_escape, text)
    return result.encode("utf-8")


# =============================================================================
# JAVASCRIPT ESCAPE ENCODING
# =============================================================================
def javascript_escape_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Escape text for use in JavaScript strings.
    """
    text = _to_text(data, options)
    result = []
    for ch in text:
        code = ord(ch)
        if code < 32:
            if code == 8:
                result.append("\\b")
            elif code == 9:
                result.append("\\t")
            elif code == 10:
                result.append("\\n")
            elif code == 11:
                result.append("\\v")
            elif code == 12:
                result.append("\\f")
            elif code == 13:
                result.append("\\r")
            else:
                result.append(f"\\x{code:02X}")
        elif ch == "\\":
            result.append("\\\\")
        elif ch == "'":
            result.append("\\'")
        elif ch == '"':
            result.append('\\"')
        elif ch == "`":
            result.append("\\`")
        elif ch == "$":
            result.append("\\$")
        elif code > 126:
            result.append(f"\\u{code:04X}")
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def javascript_escape_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode JavaScript escaped text."""
    text = _to_text(data, options)
    
    def replace_escape(match):
        if match.group(1):  # \xXX
            return chr(int(match.group(1), 16))
        elif match.group(2):  # \uXXXX
            return chr(int(match.group(2), 16))
        elif match.group(3):  # \u{XXXXX}
            return chr(int(match.group(3), 16))
        elif match.group(0) == "\\b":
            return "\b"
        elif match.group(0) == "\\t":
            return "\t"
        elif match.group(0) == "\\n":
            return "\n"
        elif match.group(0) == "\\v":
            return "\v"
        elif match.group(0) == "\\f":
            return "\f"
        elif match.group(0) == "\\r":
            return "\r"
        else:
            return match.group(0)[1:]  # Remove backslash
    
    pattern = r"\\x([0-9A-Fa-f]{2})|\\u([0-9A-Fa-f]{4})|\\u\{([0-9A-Fa-f]+)\}|\\[btnvfr\\'\"`$]"
    result = re.sub(pattern, replace_escape, text)
    return result.encode("utf-8")


# =============================================================================
# SQL ESCAPE ENCODING
# =============================================================================
def sql_escape_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Escape text for use in SQL strings.
    Doubles single quotes and handles special characters.
    """
    text = _to_text(data, options)
    # SQL escape: double single quotes
    result = text.replace("'", "''")
    result = result.replace("\\", "\\\\")
    result = result.replace("\x00", "\\0")
    return result.encode("utf-8")


def sql_escape_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode SQL escaped text."""
    text = _to_text(data, options)
    # Reverse the escaping
    result = text.replace("\\\\", "\\")
    result = result.replace("\\0", "\x00")
    result = result.replace("''", "'")
    return result.encode("utf-8")


# =============================================================================
# SHELL/BASH ESCAPE ENCODING
# =============================================================================
def shell_escape_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Escape text for safe use in shell commands.
    Uses single quotes and escapes special characters.
    """
    text = _to_text(data, options)
    # Simple approach: wrap in single quotes and escape existing single quotes
    result = "'" + text.replace("'", "'\"'\"'") + "'"
    return result.encode("utf-8")


def shell_escape_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode shell escaped text."""
    text = _to_text(data, options)
    # Remove surrounding quotes and restore escaped quotes
    if text.startswith("'") and text.endswith("'"):
        text = text[1:-1]
    result = text.replace("'\"'\"'", "'")
    return result.encode("utf-8")


# =============================================================================
# LDAP ESCAPE ENCODING
# =============================================================================
def ldap_escape_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Escape text for use in LDAP queries.
    Uses backslash followed by hex code for special characters.
    """
    text = _to_text(data, options)
    result = []
    special_chars = "*()\\\x00"
    for ch in text:
        if ch in special_chars:
            result.append(f"\\{ord(ch):02X}")
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def ldap_escape_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode LDAP escaped text."""
    text = _to_text(data, options)
    
    def replace_escape(match):
        return chr(int(match.group(1), 16))
    
    result = re.sub(r"\\([0-9A-Fa-f]{2})", replace_escape, text)
    return result.encode("utf-8")


# =============================================================================
# XML ENTITY ENCODING (Full)
# =============================================================================
def xml_entity_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode text with XML entities.
    More comprehensive than basic HTML entity encoding.
    """
    text = _to_text(data, options)
    result = []
    entity_map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&apos;",
    }
    for ch in text:
        result.append(entity_map.get(ch, ch))
    return "".join(result).encode("utf-8")


def xml_entity_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode XML entities."""
    text = _to_text(data, options)
    # Named entities
    entity_map = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&apos;": "'",
    }
    result = text
    for entity, char in entity_map.items():
        result = result.replace(entity, char)
    
    # Numeric entities &#NN;
    def replace_numeric(match):
        return chr(int(match.group(1)))
    result = re.sub(r"&#(\d+);", replace_numeric, result)
    
    # Hex entities &#xHH;
    def replace_hex(match):
        return chr(int(match.group(1), 16))
    result = re.sub(r"&#x([0-9A-Fa-f]+);", replace_hex, result)
    
    return result.encode("utf-8")


# =============================================================================
# JWT (JSON Web Token) ENCODING/DECODING
# =============================================================================
def jwt_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data as a JWT payload (Base64URL encoded JSON).
    Creates a minimal JWT structure.
    """
    import base64
    import time
    
    # Create JWT header
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(
        json.dumps(header, separators=(",", ":")).encode()
    ).rstrip(b"=").decode()
    
    # Create JWT payload
    payload_data = _to_text(data, options)
    payload = {
        "data": payload_data,
        "iat": int(options.get("iat", time.time())),
    }
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).rstrip(b"=").decode()
    
    # Create signature (fake for encoding purposes)
    signature = "signature"
    
    jwt_token = f"{header_b64}.{payload_b64}.{signature}"
    return jwt_token.encode("ascii")


def jwt_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode JWT and extract payload data.
    """
    import base64
    
    token = _to_text(data, options)
    parts = token.split(".")
    
    if len(parts) != 3:
        raise ValueError("Invalid JWT format")
    
    # Decode payload
    payload_b64 = parts[1]
    # Add padding
    padding = "=" * ((4 - len(payload_b64) % 4) % 4)
    payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode("utf-8")
    payload = json.loads(payload_json)
    
    # Extract data
    return payload.get("data", "").encode("utf-8")


# =============================================================================
# URL PARAMETER ENCODING (Query String)
# =============================================================================
def url_param_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data as URL query parameter value.
    """
    text = _to_text(data, options)
    key = options.get("key", "data")
    encoded_value = urllib.parse.quote(text, safe="")
    return f"{key}={encoded_value}".encode("ascii")


def url_param_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode URL query parameter and extract value.
    """
    text = _to_text(data, options)
    if "=" in text:
        _, value = text.split("=", 1)
        return urllib.parse.unquote(value).encode("utf-8")
    return urllib.parse.unquote(text).encode("utf-8")


# =============================================================================
# DATA URI ENCODING
# =============================================================================
def data_uri_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Encode data as a Data URI.
    """
    import base64
    
    mime_type = options.get("mime", "text/plain")
    encoding = options.get("encoding_type", "base64")
    
    if encoding == "base64":
        encoded = base64.b64encode(data).decode("ascii")
        return f"data:{mime_type};base64,{encoded}".encode("ascii")
    else:
        # URL encoded
        encoded = urllib.parse.quote(data.decode("utf-8", errors="replace"))
        return f"data:{mime_type},{encoded}".encode("ascii")


def data_uri_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Decode Data URI and extract original data.
    """
    import base64
    
    uri = _to_text(data, options)
    
    if not uri.startswith("data:"):
        raise ValueError("Not a valid Data URI")
    
    # Parse Data URI
    match = re.match(r"data:([^;]+);?([^,]*),(.+)", uri)
    if not match:
        raise ValueError("Invalid Data URI format")
    
    mime_type, encoding, content = match.groups()
    
    if encoding == "base64":
        return base64.b64decode(content)
    else:
        return urllib.parse.unquote(content).encode("utf-8")


# =============================================================================
# MARKDOWN ESCAPE ENCODING
# =============================================================================
def markdown_escape_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Escape special Markdown characters.
    """
    text = _to_text(data, options)
    special_chars = r"\`*_{}[]()#+-.!|"
    result = []
    for ch in text:
        if ch in special_chars:
            result.append(f"\\{ch}")
        else:
            result.append(ch)
    return "".join(result).encode("utf-8")


def markdown_escape_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode Markdown escaped text."""
    text = _to_text(data, options)
    result = []
    i = 0
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text):
            result.append(text[i + 1])
            i += 2
        else:
            result.append(text[i])
            i += 1
    return "".join(result).encode("utf-8")


# =============================================================================
# LATEX ESCAPE ENCODING
# =============================================================================
def latex_escape_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Escape text for use in LaTeX documents.
    """
    text = _to_text(data, options)
    result = []
    escape_map = {
        "\\": "\\textbackslash{}",
        "{": "\\{",
        "}": "\\}",
        "$": "\\$",
        "&": "\\&",
        "#": "\\#",
        "%": "\\%",
        "_": "\\_",
        "^": "\\^{}",
        "~": "\\textasciitilde{}",
        "|": "\\textbar{}",
        "<": "\\textless{}",
        ">": "\\textgreater{}",
    }
    for ch in text:
        result.append(escape_map.get(ch, ch))
    return "".join(result).encode("utf-8")


def latex_escape_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """Decode LaTeX escaped text (best effort)."""
    text = _to_text(data, options)
    result = text
    # Reverse replacements
    replacements = [
        ("\\textbackslash{}", "\\"),
        ("\\{", "{"),
        ("\\}", "}"),
        ("\\$", "$"),
        ("\\&", "&"),
        ("\\#", "#"),
        ("\\%", "%"),
        ("\\_", "_"),
        ("\\^{}", "^"),
        ("\\textasciitilde{}", "~"),
        ("\\textbar{}", "|"),
        ("\\textless{}", "<"),
        ("\\textgreater{}", ">"),
    ]
    for escaped, original in replacements:
        result = result.replace(escaped, original)
    return result.encode("utf-8")


def get_specs() -> list[MethodSpec]:
    return [
        # Web escaping
        MethodSpec("css_escape", "web_advanced", "CSS escape sequences", css_escape_encode, css_escape_decode, aliases=("css",)),
        MethodSpec("javascript_escape", "web_advanced", "JavaScript string escape", javascript_escape_encode, javascript_escape_decode, aliases=("js_escape", "js")),
        MethodSpec("sql_escape", "web_advanced", "SQL string escape", sql_escape_encode, sql_escape_decode, aliases=("sql",)),
        MethodSpec("shell_escape", "web_advanced", "Shell/Bash escape", shell_escape_encode, shell_escape_decode, aliases=("bash", "sh")),
        MethodSpec("ldap_escape", "web_advanced", "LDAP query escape", ldap_escape_encode, ldap_escape_decode, aliases=("ldap",)),
        
        # Markup
        MethodSpec("xml_entity", "web_advanced", "XML entity encoding", xml_entity_encode, xml_entity_decode),
        MethodSpec("markdown_escape", "web_advanced", "Markdown escape", markdown_escape_encode, markdown_escape_decode, aliases=("md",)),
        MethodSpec("latex_escape", "web_advanced", "LaTeX escape", latex_escape_encode, latex_escape_decode, aliases=("tex",)),
        
        # Network/Transport
        MethodSpec("jwt", "web_advanced", "JSON Web Token", jwt_encode, jwt_decode, aliases=("json_web_token",)),
        MethodSpec("url_param", "web_advanced", "URL query parameter", url_param_encode, url_param_decode, aliases=("query_param",)),
        MethodSpec("data_uri", "web_advanced", "Data URI encoding", data_uri_encode, data_uri_decode, aliases=("dataurl",)),
    ]
