from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from typing import Any

from .exceptions import SecurityPolicyError


SECRET_KEY_RE = re.compile(r"(api[_-]?key|token|secret|password)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(
    r"(Bearer\s+)[A-Za-z0-9._~+/=-]+|"
    r"(OMNI_API_KEY=)[^\s]+|"
    r"([?&](?:api[_-]?key|token|secret|password)=)[^&\s]+",
    re.IGNORECASE,
)


def contains_secret_key(key: Any) -> bool:
    return isinstance(key, str) and bool(SECRET_KEY_RE.search(key))


def find_secret_keys(payload: Any, prefix: str = "") -> list[str]:
    matches: list[str] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if contains_secret_key(key):
                matches.append(path)
            matches.extend(find_secret_keys(value, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            matches.extend(find_secret_keys(value, f"{prefix}[{index}]"))
    return matches


def reject_secret_keys(payload: Any, *, source: str) -> None:
    keys = find_secret_keys(payload)
    if keys:
        joined = ", ".join(sorted(keys))
        raise SecurityPolicyError(
            f"Secret-like keys are not allowed in {source}: {joined}. "
            "Use environment variables or a secret manager instead."
        )


def redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        redacted = {}
        for key, item in value.items():
            redacted[key] = "[REDACTED]" if contains_secret_key(key) else redact(item)
        return redacted
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return SECRET_VALUE_RE.sub(lambda match: _redact_match(match), value)
    return value


def _redact_match(match: re.Match[str]) -> str:
    for index in range(1, len(match.groups()) + 1):
        prefix = match.group(index)
        if prefix:
            return f"{prefix}[REDACTED]"
    return "[REDACTED]"


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.getMessage())
        record.args = ()
        return True

