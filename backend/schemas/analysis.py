"""
Project: AlphaQuant AI
File: backend/schemas/analysis.py
Description: AI stock analysis request and response schemas.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from backend.core.config.settings import AIProviderName
from backend.schemas.common import ORMModel


class StockAnalysisRequest(ORMModel):
    """Request schema for AI stock analysis."""

    symbol: str = Field(min_length=1, max_length=32)
    market: Literal["A", "HK", "US"] = Field(default="A")
    provider: AIProviderName | None = Field(default=None)
    include_news: bool = Field(default=True)
    include_announcements: bool = Field(default=True)
    include_financials: bool = Field(default=True)
    lookback_days: int = Field(default=120, ge=20, le=1000)
    model: str | None = Field(default=None)
    api_base_url: str | None = Field(default=None)
    api_key: str | None = Field(default=None)


class StockAnalysisResponse(ORMModel):
    """Response schema for AI stock analysis."""

    symbol: str
    market: str
    provider: str
    model: str
    report_markdown: str
    objective_data: dict[str, object]
    technical_summary: dict[str, object]
    risk_summary: dict[str, object]
    data_timestamp: datetime

