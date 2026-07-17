"""
Project: AlphaQuant AI
File: backend/ai/providers/base.py
Description: Unified AI provider protocol and shared request/response models.
Python Version: 3.11.9
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, Field

from backend.core.config.settings import AIProviderName


class AIMessage(BaseModel):
    """Chat message used by AI providers."""

    role: Literal["system", "user", "assistant"] = Field(description="Message role.")
    content: str = Field(min_length=1, description="Message content.")


class AICompletionRequest(BaseModel):
    """Unified AI completion request."""

    messages: list[AIMessage]
    model: str
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)


class AICompletionResponse(BaseModel):
    """Unified AI completion response."""

    provider: AIProviderName
    model: str
    content: str
    raw_response: dict[str, object]


class AIProvider(ABC):
    """Abstract AI provider interface."""

    provider_name: AIProviderName

    @abstractmethod
    async def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        """
        Execute a chat completion request.

        Args:
            request: Unified completion request.

        Returns:
            Unified completion response.
        """

    @abstractmethod
    async def close(self) -> None:
        """Close provider resources."""


def messages_to_openai_payload(messages: Sequence[AIMessage]) -> list[dict[str, str]]:
    """
    Convert unified messages to OpenAI-compatible payload messages.

    Args:
        messages: Unified AI messages.

    Returns:
        OpenAI-compatible message dictionaries.
    """
    return [{"role": message.role, "content": message.content} for message in messages]

