from __future__ import annotations

from typing import Any


def annotation_lines(issues: list[dict[str, Any]]) -> list[str]:
    lines = []
    for issue in issues:
        level = "error" if issue.get("severity") == "error" or issue.get("risk") == "breaking" else "warning"
        file_path = issue.get("file") or "omniflow"
        message = str(issue.get("message") or issue.get("summary") or "OmniFlow issue").replace("\n", " ")
        lines.append(f"::{level} file={file_path},line=1::{message}")
    return lines

