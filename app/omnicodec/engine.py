from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import AppConfig
from .detect import detect_candidates
from .io_manager import IOManager
from .methods import ALL_SPEC_LOADERS
from .models import MethodSpec
from .registry import MethodRegistry


@dataclass(slots=True)
class TransformResult:
    method: str
    mode: str
    output: bytes
    output_path: Path | None


class OmniCodecEngine:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig.load()
        self.registry = MethodRegistry()
        self.io = IOManager(self.config.output_dir)
        self._load_methods()

    def _load_methods(self) -> None:
        for loader in ALL_SPEC_LOADERS:
            for spec in loader():
                self.registry.add(spec)

    def list_methods(self) -> list[MethodSpec]:
        return self.registry.list_methods()

    def categories(self) -> dict[str, list[MethodSpec]]:
        return self.registry.categories()

    def detect(self, data: bytes) -> list[str]:
        return detect_candidates(data)

    def run(
        self,
        *,
        method_key: str,
        mode: str,
        input_data: bytes,
        options: dict[str, Any] | None = None,
        expected: bytes | None = None,
        autosave: bool | None = None,
    ) -> TransformResult:
        options = options or {}
        spec = self.registry.get(method_key)
        out_path: Path | None = None

        if mode == "encode":
            if spec.encode is None:
                raise ValueError(f"Method '{spec.key}' does not support encode mode")
            output = spec.encode(input_data, options)
        elif mode == "decode":
            if spec.decode is None:
                raise ValueError(f"Method '{spec.key}' does not support decode mode")
            output = spec.decode(input_data, options)
        elif mode == "verify":
            if spec.verify is None:
                raise ValueError(f"Method '{spec.key}' does not support verify mode")
            if expected is None:
                raise ValueError("Verify mode requires expected bytes")
            ok = spec.verify(input_data, expected, options)
            output = ("OK" if ok else "FAIL").encode("ascii")
        else:
            raise ValueError("mode must be one of: encode, decode, verify")

        should_save = self.config.auto_save if autosave is None else autosave
        if should_save and mode != "verify":
            ext = spec.extensions[0] if spec.extensions else ".txt"
            out_path = self.io.auto_output_path(spec.key, mode, ext)
            self.io.save_output(output, out_path)

        return TransformResult(method=spec.key, mode=mode, output=output, output_path=out_path)
