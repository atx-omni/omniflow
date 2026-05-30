from __future__ import annotations

from pathlib import Path
from typing import Any


def render_markdown_report(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# OmniFlow Report",
        "",
        f"- Tool version: `{report.get('tool_version', 'unknown')}`",
        f"- Generated at: `{report.get('generated_at', '')}`",
        f"- Git SHA: `{report.get('git_sha', '')}`",
        f"- Git branch: `{report.get('git_branch', '')}`",
        f"- Model ID: `{report.get('model_id', '')}`",
        f"- Branch: `{report.get('branch_name') or report.get('branch_id') or ''}`",
        f"- Config hash: `{report.get('config_hash', '')}`",
        f"- Policy decision: `{report.get('policy_decision', '')}`",
        f"- Exit code reason: `{report.get('exit_code_reason', '')}`",
        "",
        "## Summary",
        "",
        f"- Total issues: `{summary.get('total_issues', 0)}`",
        f"- Errors: `{summary.get('errors', 0)}`",
        f"- Warnings: `{summary.get('warnings', 0)}`",
        f"- New issues: `{summary.get('new_issues', 0)}`",
        f"- Existing issues: `{summary.get('existing_issues', 0)}`",
        f"- Resolved issues: `{summary.get('resolved_issues', 0)}`",
        f"- Risk level: `{summary.get('risk_level', 'info')}`",
        "",
        "## Issues",
        "",
    ]
    issues = report.get("issues", [])
    if not issues:
        lines.append("_No issues._")
    for issue in issues[:50]:
        severity = issue.get("severity") or issue.get("risk") or "info"
        location = issue.get("file") or issue.get("yaml_path") or issue.get("field") or issue.get("name") or ""
        lines.append(f"- **{severity}** `{location}` {issue.get('message') or issue.get('summary') or ''}")
    lines.append("")
    return "\n".join(lines)


def write_markdown_report(path: str | Path, report: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_markdown_report(report), encoding="utf-8")

