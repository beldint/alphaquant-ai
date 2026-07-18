"""
Project: AlphaQuant AI
File: backend/ai/providers/http.py
Description: Shared HTTP implementation for AI providers.
Python Version: 3.11.9
"""

from __future__ import annotations

from typing import Any

import httpx
from loguru import logger

from backend.ai.providers.base import (
    AICompletionRequest,
    AICompletionResponse,
    AIProvider,
    messages_to_openai_payload,
)
from backend.core.config.settings import AIProviderName
from backend.core.exceptions import AIException, NetworkException
from backend.datasource.providers.http_client import build_async_client


class OpenAICompatibleProvider(AIProvider):
    """Provider implementation for OpenAI-compatible chat completion APIs."""

    def __init__(
        self,
        *,
        provider_name: AIProviderName,
        api_key: str,
        base_url: str,
        timeout_seconds: float,
        default_model: str,
    ) -> None:
        """
        Initialize an OpenAI-compatible provider.

        Args:
            provider_name: Provider identity.
            api_key: Provider API key.
            base_url: Provider base URL.
            timeout_seconds: HTTP timeout in seconds.
            default_model: Fallback model name.
        """
        self.provider_name = provider_name
        self.default_model = default_model
        self.client = build_async_client(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    async def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        """
        Execute a chat completion request.

        Args:
            request: Unified completion request.

        Returns:
            Unified completion response.
        """
        payload = {
            "model": request.model or self.default_model,
            "messages": messages_to_openai_payload(request.messages),
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            logger.exception(
                "AI provider request failed: provider={provider}",
                provider=self.provider_name.value,
            )
            raise NetworkException(
                "AI provider network request failed",
                method="POST",
                url="/chat/completions",
                cause=exc,
            ) from exc
        except ValueError as exc:
            raise AIException(
                "AI provider returned invalid JSON",
                provider=self.provider_name.value,
                cause=exc,
            ) from exc

        content = self._extract_content(data)
        return AICompletionResponse(
            provider=self.provider_name,
            model=str(data.get("model", payload["model"])),
            content=content,
            raw_response=data,
        )

    async def close(self) -> None:
        """Close HTTP client resources."""
        await self.client.aclose()

    def _extract_content(self, data: dict[str, Any]) -> str:
        """
        Extract assistant content from an OpenAI-compatible response.

        Args:
            data: Provider response JSON.

        Returns:
            Assistant content.

        Raises:
            AIException: If response format is invalid.
        """
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise AIException(
                "AI provider response missing choices",
                provider=self.provider_name.value,
            )
        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise AIException(
                "AI provider choice is invalid",
                provider=self.provider_name.value,
            )
        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise AIException(
                "AI provider response missing message",
                provider=self.provider_name.value,
            )
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise AIException(
                "AI provider response content is empty",
                provider=self.provider_name.value,
            )
        return content
