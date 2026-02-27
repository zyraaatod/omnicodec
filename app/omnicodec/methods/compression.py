from __future__ import annotations

import bz2
import gzip
import lzma
import zlib
from typing import Any

from ..models import MethodSpec


def gzip_encode(data: bytes, options: dict[str, Any]) -> bytes:
    level = int(options.get("level", 6))
    return gzip.compress(data, compresslevel=level)


def gzip_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return gzip.decompress(data)


def zlib_encode(data: bytes, options: dict[str, Any]) -> bytes:
    level = int(options.get("level", 6))
    return zlib.compress(data, level=level)


def zlib_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return zlib.decompress(data)


def deflate_encode(data: bytes, options: dict[str, Any]) -> bytes:
    level = int(options.get("level", 6))
    comp = zlib.compressobj(level=level, wbits=-zlib.MAX_WBITS)
    return comp.compress(data) + comp.flush()


def deflate_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return zlib.decompress(data, wbits=-zlib.MAX_WBITS)


def bzip2_encode(data: bytes, options: dict[str, Any]) -> bytes:
    level = int(options.get("level", 9))
    return bz2.compress(data, compresslevel=level)


def bzip2_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return bz2.decompress(data)


def xz_encode(data: bytes, options: dict[str, Any]) -> bytes:
    level = int(options.get("preset", 6))
    return lzma.compress(data, preset=level)


def xz_decode(data: bytes, options: dict[str, Any]) -> bytes:
    return lzma.decompress(data)


def get_specs() -> list[MethodSpec]:
    return [
        MethodSpec("gzip", "compression", "Gzip compression", gzip_encode, gzip_decode, extensions=(".gz",)),
        MethodSpec("zlib", "compression", "Zlib compression", zlib_encode, zlib_decode),
        MethodSpec("deflate", "compression", "Raw DEFLATE stream", deflate_encode, deflate_decode),
        MethodSpec("bzip2", "compression", "Bzip2 compression", bzip2_encode, bzip2_decode, aliases=("bz2",), extensions=(".bz2",)),
        MethodSpec("xz", "compression", "XZ / LZMA compression", xz_encode, xz_decode, aliases=("lzma",), extensions=(".xz",)),
    ]
