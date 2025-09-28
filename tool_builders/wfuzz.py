"""wfuzz tool builder."""
from __future__ import annotations

from . import ToolTemplate, registry


def build(method: str, url: str, headers: dict[str, str], body: str) -> ToolTemplate:
    cmd = f"wfuzz -c -w /usr/share/seclists/Fuzzing/special-chars.txt -u \"{url}\""
    if method.upper() != "GET":
        cmd += f" -X {method.upper()}"
    if body:
        cmd += f" -d \"{body}\""
    for k, v in headers.items():
        if k.lower() != "host":
            cmd += f" -H \"{k}: {v}\""

    return ToolTemplate(
        title="===== wfuzz コマンド =====",
        command=cmd,
        tip="👉 Replace value with 'FUZZ' to test injection points.",
    )


registry.register("wfuzz", build)
