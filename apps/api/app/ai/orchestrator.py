"""SOP Orchestrator — coordinates chunking, summarization, and final generation."""
from __future__ import annotations

import asyncio

from app.ai.azure_client import AzureOpenAIClient, get_ai_client
from app.ai.chunker import chunk_text, count_tokens
from app.ai.formatter import ensure_h1, extract_title, split_sections
from app.ai.prompts import (
    SYSTEM_PROMPT_SOP,
    build_chunk_summary_prompt,
    build_refinement_prompt,
    build_sop_prompt,
)
from app.core.logging import get_logger
from app.schemas.sop import SOPSection
from app.utils.sanitizer import neutralize_injection, sanitize_transcript

logger = get_logger(__name__)


class SOPGenerationResult:
    def __init__(self, *, title: str, markdown: str, sections: list[SOPSection], tokens_used: int) -> None:
        self.title = title
        self.markdown = markdown
        self.sections = sections
        self.tokens_used = tokens_used


class SOPOrchestrator:
    """End-to-end transcript → SOP pipeline."""

    def __init__(self, client: AzureOpenAIClient | None = None) -> None:
        self.client = client or get_ai_client()

    async def generate(
        self,
        *,
        transcript: str,
        title: str | None = None,
        instructions: str | None = None,
    ) -> SOPGenerationResult:
        cleaned = neutralize_injection(sanitize_transcript(transcript))
        token_count = count_tokens(cleaned)
        logger.info("sop_generation_start", tokens=token_count)

        chunks = chunk_text(cleaned)
        summaries = await self._summarize_chunks(chunks)
        prompt = build_sop_prompt(title=title, summaries=summaries, custom_instructions=instructions)

        markdown, tokens = await self.client.complete(
            system_prompt=SYSTEM_PROMPT_SOP,
            user_prompt=prompt,
        )

        final_title = title or extract_title(markdown)
        markdown = ensure_h1(markdown, final_title)
        sections = split_sections(markdown)

        logger.info("sop_generation_done", tokens=tokens, sections=len(sections))
        return SOPGenerationResult(
            title=final_title,
            markdown=markdown,
            sections=sections,
            tokens_used=tokens,
        )

    async def _summarize_chunks(self, chunks: list[str]) -> list[str]:
        if len(chunks) == 1:
            return chunks

        async def _one(idx: int, chunk: str) -> str:
            content, _ = await self.client.complete(
                system_prompt="You extract operational facts. Be precise. Bulleted output only.",
                user_prompt=build_chunk_summary_prompt(chunk, idx, len(chunks)),
                max_tokens=1024,
            )
            return content

        # bounded concurrency to avoid rate limit storms
        semaphore = asyncio.Semaphore(4)

        async def _bounded(idx: int, chunk: str) -> str:
            async with semaphore:
                return await _one(idx, chunk)

        return await asyncio.gather(*(_bounded(i, c) for i, c in enumerate(chunks)))

    async def refine_stream(self, *, current_sop: str, user_message: str):
        """Stream a refinement of an existing SOP."""
        prompt = build_refinement_prompt(current_sop, user_message)
        async for token in self.client.stream(
            system_prompt=SYSTEM_PROMPT_SOP,
            user_prompt=prompt,
        ):
            yield token
