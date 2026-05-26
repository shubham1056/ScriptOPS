"""Azure OpenAI GPT-5 async client with retry + streaming."""
from __future__ import annotations

from collections.abc import AsyncIterator

from openai import AsyncAzureOpenAI
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)

_RETRYABLE = (APIConnectionError, APITimeoutError, RateLimitError)


class AzureOpenAIClient:
    """Thin async wrapper around Azure OpenAI with retries and streaming."""

    def __init__(self) -> None:
        if not settings.AZURE_OPENAI_API_KEY or not settings.AZURE_OPENAI_ENDPOINT:
            logger.warning("azure_openai_not_configured")
        self._client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY or "missing",
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT or "https://missing.openai.azure.com",
            api_version=settings.AZURE_OPENAI_API_VERSION,
            timeout=settings.AZURE_OPENAI_TIMEOUT_SECONDS,
        )
        self._deployment = settings.AZURE_OPENAI_DEPLOYMENT

    @retry(
        retry=retry_if_exception_type(_RETRYABLE),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> tuple[str, int]:
        """Non-streaming completion. Returns (content, tokens_used)."""
        try:
            response = await self._client.chat.completions.create(
                model=self._deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature if temperature is not None else settings.AZURE_OPENAI_TEMPERATURE,
                max_completion_tokens=max_tokens or settings.AZURE_OPENAI_MAX_TOKENS,
            )
        except APIError as exc:
            logger.error("azure_openai_error", error=str(exc))
            raise AIServiceError(f"Azure OpenAI error: {exc}") from exc

        choice = response.choices[0]
        content = (choice.message.content or "").strip()
        tokens_used = response.usage.total_tokens if response.usage else 0
        return content, tokens_used

    async def stream(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Yield content tokens as they stream from Azure OpenAI."""
        try:
            stream = await self._client.chat.completions.create(
                model=self._deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature if temperature is not None else settings.AZURE_OPENAI_TEMPERATURE,
                max_completion_tokens=max_tokens or settings.AZURE_OPENAI_MAX_TOKENS,
                stream=True,
            )
        except APIError as exc:
            logger.error("azure_openai_stream_error", error=str(exc))
            raise AIServiceError(f"Azure OpenAI stream error: {exc}") from exc

        async for event in stream:
            if not event.choices:
                continue
            delta = event.choices[0].delta
            if delta and delta.content:
                yield delta.content


_singleton: AzureOpenAIClient | None = None


def get_ai_client() -> AzureOpenAIClient:
    global _singleton
    if _singleton is None:
        _singleton = AzureOpenAIClient()
    return _singleton
