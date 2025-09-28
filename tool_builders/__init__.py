"""Tool builders for converting HTTP requests into tool-specific commands."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict


@dataclass(frozen=True)
class ToolTemplate:
    """Represents printable information for a tool command."""

    title: str
    command: str
    tip: str | None = None


Builder = Callable[[str, str, dict[str, str], str], ToolTemplate]


class ToolRegistry:
    """Registry that keeps the mapping of tool names to builder callables."""

    def __init__(self) -> None:
        self._builders: Dict[str, Builder] = {}

    def register(self, name: str, builder: Builder) -> None:
        if name in self._builders:
            raise ValueError(f"Tool '{name}' is already registered")
        self._builders[name] = builder

    def build(self, name: str, method: str, url: str, headers: dict[str, str], body: str) -> ToolTemplate:
        try:
            builder = self._builders[name]
        except KeyError as exc:
            raise ValueError(f"Unsupported tool: {name}") from exc
        return builder(method, url, headers, body)

    def choices(self) -> list[str]:
        return sorted(self._builders)


registry = ToolRegistry()


# Ensure default tool builders are registered on import.
from . import wfuzz as _wfuzz  # noqa: F401
from . import sqlmap as _sqlmap  # noqa: F401


__all__ = ["ToolTemplate", "registry"]
