from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


TransformFn = Callable[[bytes, dict[str, Any]], bytes]
VerifyFn = Callable[[bytes, bytes, dict[str, Any]], bool]


@dataclass(slots=True)
class MethodSpec:
    key: str
    category: str
    description: str
    encode: TransformFn | None = None
    decode: TransformFn | None = None
    verify: VerifyFn | None = None
    aliases: tuple[str, ...] = field(default_factory=tuple)
    extensions: tuple[str, ...] = field(default_factory=tuple)

    @property
    def reversible(self) -> bool:
        return self.encode is not None and self.decode is not None

    @property
    def verify_only(self) -> bool:
        return self.verify is not None and not self.reversible
