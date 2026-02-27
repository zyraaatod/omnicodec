from __future__ import annotations

import csv
import io
import json
import tomllib
import xml.etree.ElementTree as ET
from typing import Any

from ..models import MethodSpec


def json_encode(data: bytes, options: dict[str, Any]) -> bytes:
    obj = data.decode("utf-8", errors="strict")
    pretty = bool(options.get("pretty", True))
    payload = {"data": obj}
    if pretty:
        return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def json_decode(data: bytes, options: dict[str, Any]) -> bytes:
    payload = json.loads(data.decode("utf-8"))
    if isinstance(payload, dict) and "data" in payload:
        return str(payload["data"]).encode("utf-8")
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def xml_encode(data: bytes, options: dict[str, Any]) -> bytes:
    root = ET.Element("payload")
    root.text = data.decode("utf-8", errors="replace")
    return ET.tostring(root, encoding="utf-8")


def xml_decode(data: bytes, options: dict[str, Any]) -> bytes:
    root = ET.fromstring(data)
    return (root.text or "").encode("utf-8")


def csv_encode(data: bytes, options: dict[str, Any]) -> bytes:
    text = data.decode("utf-8", errors="replace")
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([text])
    return out.getvalue().encode("utf-8")


def csv_decode(data: bytes, options: dict[str, Any]) -> bytes:
    text = data.decode("utf-8", errors="replace")
    row = next(csv.reader(io.StringIO(text)), [""])
    return (row[0] if row else "").encode("utf-8")


def toml_encode(data: bytes, options: dict[str, Any]) -> bytes:
    text = data.decode("utf-8", errors="replace")
    escaped = text.replace("\n", "\\n").replace('"', '\\"')
    return f'data = "{escaped}"\n'.encode("utf-8")


def toml_decode(data: bytes, options: dict[str, Any]) -> bytes:
    obj = tomllib.loads(data.decode("utf-8"))
    value = obj.get("data", "")
    return str(value).encode("utf-8")


def get_specs() -> list[MethodSpec]:
    return [
        MethodSpec("json", "serialization", "Wrap text payload in JSON", json_encode, json_decode),
        MethodSpec("xml", "serialization", "Wrap text payload in XML", xml_encode, xml_decode),
        MethodSpec("csv", "serialization", "Single-cell CSV escaping", csv_encode, csv_decode),
        MethodSpec("toml", "serialization", "Wrap text payload in TOML", toml_encode, toml_decode),
    ]
