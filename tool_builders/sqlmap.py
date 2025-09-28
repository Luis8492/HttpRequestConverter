"""sqlmap tool builder."""
from __future__ import annotations

from . import ToolTemplate, registry


def build(method: str, url: str, headers: dict[str, str], body: str) -> ToolTemplate:
    cmd = f"sqlmap -u \"{url}\""

    if method.upper() != "GET":
        cmd += f" --method={method.upper()}"

    if body:
        cmd += f" --data=\"{body}\""

    if "User-Agent" in headers:
        cmd += f" -A \"{headers['User-Agent']}\""
    if "Cookie" in headers:
        cmd += f" --cookie=\"{headers['Cookie']}\""
    if "Referer" in headers:
        cmd += f" --referer=\"{headers['Referer']}\""
    if "Host" in headers:
        cmd += f" --host=\"{headers['Host']}\""

    extra_headers = []
    for k, v in headers.items():
        if k not in ["User-Agent", "Cookie", "Referer", "Host"]:
            extra_headers.append(f"{k}: {v}")
    if extra_headers:
        header_str = "\\n".join(extra_headers)
        cmd += f" --headers=\"{header_str}\""

    cmd += " --level=5 --risk=3"

    return ToolTemplate(
        title="===== sqlmap コマンド =====",
        command=cmd,
        tip="👉 Insert '*' at desired injection point (e.g., TrackingId=abc*).",
    )


registry.register("sqlmap", build)
