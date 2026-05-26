"""Reusable prompt templates for SOP generation."""
from __future__ import annotations

from app.constants import SOP_SECTIONS

SYSTEM_PROMPT_SOP = """You are TranscribeOP, an enterprise SOP authoring assistant.
You convert raw transcripts and operational discussions into precise, audit-ready
Standard Operating Procedures (SOPs).

Hard rules:
- Output strictly valid Markdown.
- Use clear, neutral, professional language. No marketing tone.
- Do not invent procedures that are not supported by the source.
- If a section cannot be derived from the source, write: "_Not specified in source._"
- Number every step. Be explicit about actors, systems, and expected outcomes.
- Prefer imperative voice ("Click Save", "Run the migration").
- Never include the original raw transcript verbatim.
"""

SOP_SECTIONS_TEMPLATE = "\n".join(f"## {s}" for s in SOP_SECTIONS)


def build_chunk_summary_prompt(chunk: str, index: int, total: int) -> str:
    return f"""You are summarizing chunk {index + 1} of {total} of a transcript.
Extract ONLY operational content useful for a Standard Operating Procedure:
- actors and roles
- systems / tools mentioned
- step-by-step actions
- prerequisites, risks, validation steps
- troubleshooting notes

Output a concise bulleted list. No prose, no preamble.

CHUNK:
\"\"\"
{chunk}
\"\"\"
"""


def build_sop_prompt(
    *,
    title: str | None,
    summaries: list[str],
    custom_instructions: str | None,
) -> str:
    joined = "\n\n---\n\n".join(f"### Summary {i + 1}\n{s}" for i, s in enumerate(summaries))
    extra = f"\n\nADDITIONAL INSTRUCTIONS FROM AUTHOR:\n{custom_instructions}\n" if custom_instructions else ""
    title_hint = f'Use this title verbatim: "{title}"' if title else "Derive a precise SOP title from the content."

    return f"""Generate a complete, enterprise-grade Standard Operating Procedure.

{title_hint}

Use EXACTLY these top-level sections, in this order, formatted as H2 Markdown headings:

{SOP_SECTIONS_TEMPLATE}

Source material (pre-summarized chunks):
{joined}
{extra}

Return ONLY the Markdown SOP. Do not wrap in code fences. Do not add commentary."""


def build_refinement_prompt(current_sop: str, user_message: str) -> str:
    return f"""The user wants to refine the following SOP. Apply their request and
return the FULL updated SOP in Markdown.

CURRENT SOP:
\"\"\"
{current_sop}
\"\"\"

USER REQUEST:
{user_message}
"""
