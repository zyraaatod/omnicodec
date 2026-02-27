from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from omnicodec.engine import OmniCodecEngine


class SmokeTests(unittest.TestCase):
    def test_base64_roundtrip(self) -> None:
        e = OmniCodecEngine()
        src = b"hello world"
        enc = e.run(method_key="base64", mode="encode", input_data=src, autosave=False).output
        dec = e.run(method_key="base64", mode="decode", input_data=enc, autosave=False).output
        self.assertEqual(dec, src)

    def test_hex_roundtrip(self) -> None:
        e = OmniCodecEngine()
        src = b"abc123"
        enc = e.run(method_key="hex", mode="encode", input_data=src, autosave=False).output
        dec = e.run(method_key="hex", mode="decode", input_data=enc, autosave=False).output
        self.assertEqual(dec, src)

    def test_sha256_verify(self) -> None:
        e = OmniCodecEngine()
        src = b"hello"
        digest = e.run(method_key="sha256", mode="encode", input_data=src, autosave=False).output
        ok = e.run(method_key="sha256", mode="verify", input_data=src, expected=digest, autosave=False).output
        self.assertEqual(ok, b"OK")


if __name__ == "__main__":
    unittest.main()
