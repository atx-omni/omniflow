from __future__ import annotations

import datetime as dt
from typing import Any

from ..omni_client import OmniClient


def parse_model_issues(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    issues = []
    for item in payload:
        is_warning = bool(item.get("is_warning"))
        issues.append(
            {
                "validator": "model",
                "severity": "warning" if is_warning else "error",
                "message": str(item.get("message") or ""),
                "yaml_path": item.get("yaml_path"),
                "auto_fix": item.get("auto_fix") if isinstance(item.get("auto_fix"), dict) else None,
            }
        )
    return issues


def run_model_validation(
    *,
    client: OmniClient,
    model_id: str,
    branch_id: str | None,
    fail_on_warnings: bool = False,
) -> tuple[dict[str, Any], int]:
    issues = parse_model_issues(client.validate_model(model_id, branch_id=branch_id))
    error_count = sum(1 for issue in issues if issue["severity"] == "error")
    warning_count = sum(1 for issue in issues if issue["severity"] == "warning")
    report = {
        "tool": "omniflow",
        "validator": "model",
        "generated_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "model_id": model_id,
        "branch_id": branch_id,
        "summary": {
            "total_issues": len(issues),
            "errors": error_count,
            "warnings": warning_count,
        },
        "issues": issues,
    }
    exit_code = 1 if error_count or (fail_on_warnings and warning_count) else 0
    return report, exit_code
