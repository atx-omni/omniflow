from __future__ import annotations

import os
import subprocess


def git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def current_sha() -> str | None:
    return os.getenv("GITHUB_SHA") or git_value("rev-parse", "HEAD")


def current_branch() -> str | None:
    return (
        os.getenv("GITHUB_HEAD_REF")
        or os.getenv("GITHUB_REF_NAME")
        or git_value("branch", "--show-current")
    )


def pr_number() -> str | None:
    return os.getenv("GITHUB_EVENT_NUMBER")


def event_name() -> str | None:
    return os.getenv("GITHUB_EVENT_NAME")
