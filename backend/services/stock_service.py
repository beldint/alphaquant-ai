"""
Project: AlphaQuant AI
File: backend/services/stock_service.py
Description: Stock market data application service.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from backend.cache.redis_client import redis_cache
from backend.core.config import settings
from backend.datasource.manager import stock_provider_manager
from backend.datasource.providers.base import KlineBar, Market, RealtimeQuote, StockIdentity


class StockService:
    """Application service for stock data queries."""

    async def search_stocks(self, keyword: str, market: Market = "A") -> list[StockIdentity]:
        """
        Search stocks using configured provider failover.

        Args:
            keyword: Stock code or name keyword.
            market: Market identifier.

        Returns:
            Matched stock identities.
        """
        return await stock_provider_manager.search_stocks(keyword, market)

    async def get_realtime_quote(self, symbol: str, market: Market = "A") -> RealtimeQuote:
        """
        Fetch realtime quote with short TTL cache.

        Args:
            symbol: Stock symbol.
            market: Market identifier.

        Returns:
            Realtime quote.
        """
        cache_key = f"quote:{market}:{symbol}"
        cached = await redis_cache.get_json(cache_key)
        if isinstance(cached, dict):
            return RealtimeQuote.model_validate(cached)
        quote = await stock_provider_manager.get_realtime_quote(symbol, market)
        await redis_cache.set_json(
            cache_key,
            quote.model_dump(mode="json"),
            ttl_seconds=settings.quote_cache_ttl_seconds,
        )
        return quote

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
        Fetch daily Kline data with TTL cache.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            start_date: Optional start date.
            end_date: Optional end date.
            adjust: Price adjustment mode.

        Returns:
            Kline bars.
        """
        cache_key = f"kline:{market}:{symbol}:{start_date}:{end_date}:{adjust}"
        cached = await redis_cache.get_json(cache_key)
        if isinstance(cached, list):
            return [KlineBar.model_validate(item) for item in cached]
        bars = await stock_provider_manager.get_daily_kline(
            symbol,
            market=market,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
        await redis_cache.set_json(
            cache_key,
            [bar.model_dump(mode="json") for bar in bars],
            ttl_seconds=settings.kline_cache_ttl_seconds,
        )
        return bars


stock_service = StockService()

