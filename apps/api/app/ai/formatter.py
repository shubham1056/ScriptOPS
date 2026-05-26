"""SOP markdown post-processor: derive title + split into sections."""
from __future__ import annotations

import re

from app.schemas.sop import SOPSection

_H1 = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_H2 = re.compile(r"^##\s+(.+?)\n([\s\S]*?)(?=^##\s+|\Z)", re.MULTILINE)


def extract_title(markdown: str, fallback: str = "Untitled SOP") -> str:
    match = _H1.search(markdown)
    if match:
        return match.group(1).strip()
    # fall back to first H2 if no H1
    h2 = _H2.search(markdown)
    return h2.group(1).strip() if h2 else fallback


def split_sections(markdown: str) -> list[SOPSection]:
    sections: list[SOPSection] = []
    for match in _H2.finditer(markdown):
        heading = match.group(1).strip()
        content = match.group(2).strip()
        sections.append(SOPSection(heading=heading, content=content))
    return sections


def ensure_h1(markdown: str, title: str) -> str:
    if _H1.search(markdown):
        return markdown
    return f"# {title}\n\n{markdown}"
