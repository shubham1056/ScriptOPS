"""Sanitization helpers for AI prompts + user inputs.

Mitigates prompt-injection vectors by stripping control chars, collapsing
whitespace, and capping length.
"""
from __future__ import annotations

import re

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_INJECTION_HINTS = re.compile(
    r"(?i)\b(ignore (all|previous|the above)|disregard (all|previous)|system prompt|you are now)\b"
)
_WHITESPACE = re.compile(r"[ \t]+")


def sanitize_transcript(text: str, *, max_chars: int = 1_500_000) -> str:
    """Sanitize transcript text for AI ingestion."""
    cleaned = _CONTROL_CHARS.sub("", text)
    cleaned = _WHITESPACE.sub(" ", cleaned)
    cleaned = cleaned.strip()
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars]
    return cleaned


def neutralize_injection(text: str) -> str:
    """Soft-neutralize obvious instruction-override phrases."""
    return _INJECTION_HINTS.sub("[redacted]", text)


def sanitize_user_message(text: str, *, max_chars: int = 8000) -> str:
    cleaned = _CONTROL_CHARS.sub("", text).strip()
    return cleaned[:max_chars]
