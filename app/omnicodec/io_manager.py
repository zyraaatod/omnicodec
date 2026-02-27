from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass(slots=True)
class IOManager:
    output_dir: Path

    def read_input(self, *, text: str | None = None, file: Path | None = None, encoding: str = "utf-8") -> bytes:
        if text is not None:
            return text.encode(encoding)
        if file is not None:
            return file.read_bytes()
        raise ValueError("Either text or file input must be provided.")

    def auto_output_path(self, method_key: str, mode: str, extension: str = ".txt") -> Path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"{mode}_{method_key}_{ts}{extension}"
        return self.output_dir / name

    def save_output(self, data: bytes, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path
