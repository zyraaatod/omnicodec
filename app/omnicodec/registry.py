from __future__ import annotations

from dataclasses import dataclass, field

from .models import MethodSpec


@dataclass
class MethodRegistry:
    _by_key: dict[str, MethodSpec] = field(default_factory=dict)
    _alias_to_key: dict[str, str] = field(default_factory=dict)

    def add(self, spec: MethodSpec) -> None:
        key = spec.key.lower()
        if key in self._by_key:
            raise ValueError(f"Method already exists: {spec.key}")
        self._by_key[key] = spec
        self._alias_to_key[key] = key
        for alias in spec.aliases:
            alias_key = alias.lower()
            if alias_key in self._alias_to_key:
                raise ValueError(f"Alias already exists: {alias}")
            self._alias_to_key[alias_key] = key

    def get(self, key: str) -> MethodSpec:
        lookup = key.lower()
        if lookup not in self._alias_to_key:
            raise KeyError(f"Unknown method: {key}")
        return self._by_key[self._alias_to_key[lookup]]

    def list_methods(self) -> list[MethodSpec]:
        return sorted(self._by_key.values(), key=lambda m: (m.category, m.key))

    def categories(self) -> dict[str, list[MethodSpec]]:
        grouped: dict[str, list[MethodSpec]] = {}
        for spec in self.list_methods():
            grouped.setdefault(spec.category, []).append(spec)
        return grouped
