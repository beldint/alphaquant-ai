"""
Project: AlphaQuant AI
File: backend/schemas/stock.py
Description: Stock market request and response schemas.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.common import DateRangeQuery, ORMModel, PaginationQuery


class StockSearchQuery(PaginationQuery):
    """Stock search query schema."""

    keyword: str = Field(min_length=1, max_length=64)
    market: Literal["A", "HK", "US"] | None = Field(default=None)


class StockResponse(ORMModel):
    """Stock master data response schema."""

    id: str
    symbol: str
    name: str
    market: str
    exchange: str
    industry: str | None
    listing_date: date | None
    currency: str
    status: str


class QuoteResponse(ORMModel):
    """Realtime quote response schema."""

    symbol: str
    name: str
    market: str
    price: Decimal
    change: Decimal
    pct_change: Decimal
    volume: Decimal
    amount: Decimal
    timestamp: datetime
    source: str


class FinancialIndicators(BaseModel):
    """Financial indicator response schema."""
    model_config = ConfigDict()
    symbol: str
    name: str
    net_profit: float | None = None
    deducted_net_profit: float | None = None
    gross_margin: float | None = None
    net_margin: float | None = None
    roe: float | None = None
    revenue: float | None = None
    revenue_growth: float | None = None
    debt_ratio: float | None = None
    current_ratio: float | None = None
    quick_ratio: float | None = None
    cash: float | None = None
    interest_debt: float | None = None
    operating_cashflow: float | None = None
    pe_ttm: float | None = None
    pb: float | None = None
    dividend_yield: float | None = None
    inventory_days: float | None = None
    ar_days: float | None = None
    goodwill: float | None = None
    pledge_ratio: float | None = None
    major_reduction: str | None = None
    auditor_change: str | None = None
    market_cap: float | None = None
    total_shares: float | None = None
    report_date: str | None = None
