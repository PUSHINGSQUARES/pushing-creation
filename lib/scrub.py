"""Redact key-shaped strings from text before printing or logging."""
import re

_PATTERNS = [
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"), "sk-ant"),
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "sk"),
    (re.compile(r"AIza[A-Za-z0-9_-]{30,}"), "AIza"),
    (re.compile(r"volc_[A-Za-z0-9]{20,}"), "volc"),
    (re.compile(r"gho_[A-Za-z0-9]{20,}"), "gho"),
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "ghp"),
    (re.compile(r"xox[bp]-[A-Za-z0-9-]{20,}"), "slack"),
    # Long base64-ish strings (>40 chars of base64 alphabet, not URLs)
    (re.compile(r"(?<![/\w])[A-Za-z0-9+/]{40,}={0,2}(?![/\w])"), "b64"),
]


def scrub(text: str) -> str:
    for pattern, kind in _PATTERNS:
        text = pattern.sub(f"[REDACTED:{kind}]", text)
    return text
