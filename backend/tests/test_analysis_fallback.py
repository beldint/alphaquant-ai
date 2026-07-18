"""
Project: AlphaQuant AI
File: backend/tests/test_analysis_fallback.py
Description: Tests for AI analysis fallback behavior.
Python Version: 3.11.9
"""

from __future__ import annotations

from backend.core.config.settings import AIProviderName
from backend.core.exceptions import ConfigurationException
from backend.services.analysis_service import analysis_service


async def test_generate_report_falls_back_when_ai_key_missing(monkeypatch) -> None:
    """Analysis report generation should not fail when AI provider config is missing."""

    async def raise_configuration_error(**_: object) -> str:
        raise ConfigurationException(
            "AI provider API key is not configured",
            setting_name="deepseek_api_key",
            details={"provider": "deepseek"},
        )

    monkeypatch.setattr(analysis_service, "_generate_report", raise_configuration_error)

    response = await analysis_service.analyze_stock(
        "000001",
        provider=AIProviderName.DEEPSEEK,
        include_financials=False,
        include_announcements=False,
    )

    assert response.symbol == "000001"
    assert "系统降级分析" in response.report_markdown
    assert response.risk_summary["ai_fallback"]["enabled"] is True
