"""
Project: AlphaQuant AI
File: backend/schemas/research.py
Description: Schemas for personal A-share AI research workflows.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import Field

from backend.schemas.common import ORMModel


class ResearchRefreshRequest(ORMModel):
    """Request schema for refreshing a stock research snapshot."""

    symbol: str = Field(min_length=1, max_length=32)
    market: Literal["A"] = Field(default="A")
    lookback_days: int = Field(default=180, ge=30, le=1000)
    include_financials: bool = Field(default=True)
    include_risks: bool = Field(default=True)


class ResearchScoreResponse(ORMModel):
    """Response schema for the 100-point research scoring system."""

    symbol: str
    name: str
    score_date: date
    fundamental_score: float
    solvency_score: float
    technical_score: float
    valuation_score: float
    risk_score: float
    total_score: float
    rating: str
    strengths: list[str]
    risks: list[str]
    suggestion: str
    data_insufficient: bool = False
    raw_breakdown: dict[str, Any]


class ResearchRefreshResponse(ORMModel):
    """Response schema for a full data refresh and analysis run."""

    symbol: str
    market: str
    refreshed_at: datetime
    price_rows: int
    financial_saved: bool
    risk_rows: int
    score: ResearchScoreResponse
