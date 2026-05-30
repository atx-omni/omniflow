from __future__ import annotations

import datetime as dt
import os
import platform
from typing import Any

from . import __version__
from .config import OmniCIConfig
from .git import current_branch, current_sha, event_name


def build_evidence(
    *,
    config: OmniCIConfig,
    branch_id: str | None,
    validation_status: str,
    policy_decision: str,
    exit_code: int,
) -> dict[str, Any]:
    return {
        "tool": "omniflow",
        "tool_version": __version__,
        "config_hash": config.hash,
        "git_sha": current_sha(),
        "git_branch": current_branch(),
        "event_type": event_name(),
        "runner": {
            "os": platform.platform(),
            "python": platform.python_version(),
            "github_actions": os.getenv("GITHUB_ACTIONS") == "true",
        },
        "omni_model_id": config.omni.model_id,
        "omni_branch_id": branch_id,
        "validation_status": validation_status,
        "policy_decision": policy_decision,
        "exit_code": exit_code,
        "timestamp": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
