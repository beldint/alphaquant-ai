"""
Project: AlphaQuant AI
File: backend/ai/providers/factory.py
Description: AI provider factory and lifecycle manager.
Python Version: 3.11.9
"""

from __future__ import annotations

from pydantic import SecretStr

from backend.ai.providers.base import AIProvider
from backend.ai.providers.http import OpenAICompatibleProvider
from backend.core.config import Settings
from backend.core.config.settings import AIProviderName
from backend.core.exceptions import ConfigurationException


class AIProviderFactory:
    """Factory that creates configured AI providers by name."""

    def __init__(self, settings: Settings) -> None:
        """
        Initialize provider factory.

        Args:
            settings: Application settings.
        """
        self.settings = settings

    def create(self, provider_name: AIProviderName | None = None) -> AIProvider:
        """
        Create an AI provider instance.

        Args:
            provider_name: Optional provider name. Defaults to configured provider.

        Returns:
            Configured AI provider.
        """
        selected = provider_name or self.settings.ai_default_provider
        if selected == AIProviderName.DEEPSEEK:
            return self._create_openai_compatible(
                AIProviderName.DEEPSEEK,
                self.settings.deepseek_api_key,
                str(self.settings.deepseek_base_url),
                self.settings.ai_analysis_model,
            )
        if selected == AIProviderName.OPENAI:
            return self._create_openai_compatible(
                AIProviderName.OPENAI,
                self.settings.openai_api_key,
                str(self.settings.openai_base_url),
                self.settings.ai_analysis_model,
            )
        if selected == AIProviderName.QWEN:
            return self._create_openai_compatible(
                AIProviderName.QWEN,
                self.settings.qwen_api_key,
                str(self.settings.qwen_base_url),
                self.settings.ai_analysis_model,
            )
        if selected == AIProviderName.KIMI:
            return self._create_openai_compatible(
                AIProviderName.KIMI,
                self.settings.kimi_api_key,
                str(self.settings.kimi_base_url),
                self.settings.ai_analysis_model,
            )
        if selected == AIProviderName.CLAUDE:
            return self._create_openai_compatible(
                AIProviderName.CLAUDE,
                self.settings.claude_api_key,
                str(self.settings.claude_base_url),
                self.settings.ai_analysis_model,
            )
        if selected == AIProviderName.GEMINI:
            return self._create_openai_compatible(
                AIProviderName.GEMINI,
                self.settings.gemini_api_key,
                str(self.settings.gemini_base_url),
                self.settings.ai_analysis_model,
            )
        raise ConfigurationException(
            "Unsupported AI provider",
            setting_name="ai_default_provider",
            details={"provider": selected.value},
        )

    def _create_openai_compatible(
        self,
        provider_name: AIProviderName,
        api_key: SecretStr | None,
        base_url: str,
        default_model: str,
    ) -> OpenAICompatibleProvider:
        """
        Create an OpenAI-compatible provider.

        Args:
            provider_name: Provider identity.
            api_key: Configured API key.
            base_url: Provider base URL.
            default_model: Default model name.

        Returns:
            Configured provider instance.

        Raises:
            ConfigurationException: If the API key is missing.
        """
        if api_key is None or not api_key.get_secret_value().strip():
            raise ConfigurationException(
                "AI provider API key is not configured",
                setting_name=f"{provider_name.value}_api_key",
                details={"provider": provider_name.value},
            )
        return OpenAICompatibleProvider(
            provider_name=provider_name,
            api_key=api_key.get_secret_value(),
            base_url=base_url,
            timeout_seconds=self.settings.ai_request_timeout_seconds,
            default_model=default_model,
        )

