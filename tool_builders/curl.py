"""curl tool builder."""
from __future__ import annotations

from . import ToolTemplate, registry


def build(method: str, url: str, headers: dict[str, str], body: str) -> ToolTemplate:
    cmd = f"curl -i -s -k -X {method.upper()} \"{url}\""

    for key, value in headers.items():
        cmd += f" -H \"{key}: {value}\""

    if body:
        cmd += f" --data-raw \"{body}\""

    return ToolTemplate(
        title="===== curl コマンド =====",
        command=cmd,
        tip="👉 Consider --data-binary for non-form payloads or remove -X for simple GET requests.",
    )


registry.register("curl", build)
