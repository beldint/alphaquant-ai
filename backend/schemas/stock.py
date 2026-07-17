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

from pydantic import Field

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


class KlineQuery(DateRangeQuery):
    """Kline query schema."""

    symbol: str = Field(min_length=1, max_length=32)
    market: Literal["A", "HK", "US"] = Field(default="A")
    frequency: Literal["1m", "5m", "15m", "30m", "60m", "daily", "weekly", "monthly"] = (
        Field(default="daily")
    )
    adjust: Literal["none", "qfq", "hfq"] = Field(default="qfq")


class KlineResponse(ORMModel):
    """Kline data response schema."""

    symbol: str
    trade_date: date
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    amount: Decimal
    source: str

