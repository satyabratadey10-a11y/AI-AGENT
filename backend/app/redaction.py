from __future__ import annotations

import re


SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)([\w-]{8,})"),
    re.compile(r"(?i)(token\s*[:=]\s*)([\w-]{8,})"),
]


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(r"\1[REDACTED]", redacted)
    return redacted
