from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import os


@dataclass
class AppConfig:
    output_dir: Path = field(default_factory=lambda: Path.home() / "omnicodec" / "output")
    auto_save: bool = True
    base64_line_width: int = 76
    gzip_level: int = 6
    max_preview_bytes: int = 512

    @classmethod
    def load(cls, path: Path | None = None) -> "AppConfig":
        if path is None:
            path = Path.home() / ".config" / "omnicodec" / "config.json"
        if not path.exists():
            cfg = cls()
            cfg.ensure_dirs()
            return cfg

        data = json.loads(path.read_text(encoding="utf-8"))
        cfg = cls(
            output_dir=Path(os.path.expandvars(data.get("output_dir", str(Path.home() / "omnicodec" / "output")))),
            auto_save=bool(data.get("auto_save", True)),
            base64_line_width=int(data.get("base64_line_width", 76)),
            gzip_level=int(data.get("gzip_level", 6)),
            max_preview_bytes=int(data.get("max_preview_bytes", 512)),
        )
        cfg.ensure_dirs()
        return cfg

    def ensure_dirs(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
