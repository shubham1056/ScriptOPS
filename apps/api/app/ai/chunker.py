"""Token-aware transcript chunker using tiktoken."""
from __future__ import annotations

import tiktoken

from app.constants import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_TOKENS,
    GPT_ENCODING_NAME,
    MAX_TRANSCRIPT_TOKENS,
)
from app.core.exceptions import ValidationError

_encoding = tiktoken.get_encoding(GPT_ENCODING_NAME)


def count_tokens(text: str) -> int:
    return len(_encoding.encode(text))


def chunk_text(
    text: str,
    *,
    chunk_tokens: int = DEFAULT_CHUNK_TOKENS,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split text into token-bounded overlapping chunks."""
    if not text.strip():
        raise ValidationError("Cannot chunk empty text.")

    tokens = _encoding.encode(text)
    if len(tokens) > MAX_TRANSCRIPT_TOKENS:
        raise ValidationError(
            f"Transcript exceeds maximum supported tokens ({MAX_TRANSCRIPT_TOKENS:,})."
        )

    if len(tokens) <= chunk_tokens:
        return [text]

    chunks: list[str] = []
    step = chunk_tokens - overlap
    for start in range(0, len(tokens), step):
        slice_tokens = tokens[start : start + chunk_tokens]
        if not slice_tokens:
            break
        chunks.append(_encoding.decode(slice_tokens))
        if start + chunk_tokens >= len(tokens):
            break
    return chunks
