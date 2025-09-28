"""ffuf tool builder."""
from __future__ import annotations

from . import ToolTemplate, registry


def build(method: str, url: str, headers: dict[str, str], body: str) -> ToolTemplate:
    cmd = f"ffuf -u \"{url}\" -w /path/to/wordlist.txt"

    if method.upper() != "GET":
        cmd += f" -X {method.upper()}"

    if body:
        cmd += f" -d \"{body}\""

    for key, value in headers.items():
        if key.lower() != "host":
            cmd += f" -H \"{key}: {value}\""

    return ToolTemplate(
        title="===== ffuf コマンド =====",
        command=cmd,
        tip="👉 Replace the target parameter with 'FUZZ' and adjust the wordlist path.",
    )


registry.register("ffuf", build)
