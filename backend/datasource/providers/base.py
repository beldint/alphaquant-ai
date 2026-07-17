"""
Project: AlphaQuant AI
File: backend/datasource/providers/base.py
Description: Unified stock data provider interface and market data schemas.
Python Version: 3.11.9
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from backend.core.config.settings import StockProviderName


Market = Literal["A", "HK", "US"]


class StockIdentity(BaseModel):
    """Unified stock identity."""

    symbol: str = Field(min_length=1)
    name: str = Field(min_length=1)
    market: Market
    exchange: str
    industry: str | None = None


class RealtimeQuote(BaseModel):
    """Unified realtime quote model."""

    symbol: str
    name: str
    market: Market
    price: Decimal
    change: Decimal
    pct_change: Decimal
    volume: Decimal
    amount: Decimal
    timestamp: datetime
    source: StockProviderName


class KlineBar(BaseModel):
    """Unified OHLCV bar model."""

    symbol: str
    market: Market
    trade_date: date
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    amount: Decimal
    source: StockProviderName


class StockProvider(ABC):
    """Abstract stock data provider interface."""

    provider_name: StockProviderName

    @abstractmethod
    async def search_stocks(self, keyword: str, market: Market = "A") -> list[StockIdentity]:
        """
        Search stocks by keyword.

        Args:
            keyword: Stock code or name keyword.
            market: Market identifier.

        Returns:
            Matched stock identities.
        """

    @abstractmethod
    async def get_realtime_quote(self, symbol: str, market: Market = "A") -> RealtimeQuote:
        """
        Fetch realtime quote data.

        Args:
            symbol: Stock symbol.
            market: Market identifier.

        Returns:
            Unified realtime quote.
        """

    @abstractmethod
    async def get_daily_kline(
        self,
        symbol: str,
        *,
        market: Market = "A",
        start_date: date | None = None,
        end_date: date | None = None,
        adjust: Literal["none", "qfq", "hfq"] = "qfq",
    ) -> list[KlineBar]:
        """
        Fetch daily Kline data.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            start_date: Optional start date.
            end_date: Optional end date.
            adjust: Price adjustment mode.

        Returns:
            Unified Kline bars.
        """

    async def close(self) -> None:
        """Close provider resources."""
        return None

