"""
Project: AlphaQuant AI
File: backend/services/stock_service.py
Description: Stock market data application service.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from loguru import logger

from backend.cache.redis_client import redis_cache
from backend.core.config import settings
from backend.core.config.settings import StockProviderName
from backend.core.exceptions import StockException
from backend.datasource.manager import stock_provider_manager
from backend.datasource.providers.base import (
    KlineBar,
    Market,
    RealtimeQuote,
    StockIdentity,
)
from backend.datasource.providers.eastmoney_provider import EastMoneyStockProvider
from backend.schemas.financial import FinancialIndicators


class StockService:
    """Application service for stock data queries."""

    async def search_stocks(
        self, keyword: str, market: Market = "A"
    ) -> list[StockIdentity]:
        """
        Search stocks using configured provider failover.

        Args:
            keyword: Stock code or name keyword.
            market: Market identifier.

        Returns:
            Matched stock identities.  When no provider can respond,
            returns an empty list.
        """
        try:
            return await stock_provider_manager.search_stocks(keyword, market)
        except (StockException, Exception) as exc:
            logger.warning(
                "Stock search unavailable: keyword={keyword} error={error}",
                keyword=keyword,
                error=str(exc),
            )
            return []

    async def get_realtime_quote(
        self, symbol: str, market: Market = "A"
    ) -> RealtimeQuote:
        """
        Fetch realtime quote with short TTL cache.

        When all providers fail, returns a placeholder quote with
        name="--" and zero values so the frontend displays "--".

        Args:
            symbol: Stock symbol.
            market: Market identifier.

        Returns:
            Realtime quote or fallback placeholder.
        """
        cache_key = f"quote:{market}:{symbol}"
        cached = await redis_cache.get_json(cache_key)
        if isinstance(cached, dict):
            try:
                return RealtimeQuote.model_validate(cached)
            except Exception:
                pass
        try:
            quote = await stock_provider_manager.get_realtime_quote(symbol, market)
            await redis_cache.set_json(
                cache_key,
                quote.model_dump(mode="json"),
                ttl_seconds=settings.quote_cache_ttl_seconds,
            )
            return quote
        except (StockException, Exception) as exc:
            logger.warning(
                "Real-time quote unavailable: symbol={symbol} error={error}",
                symbol=symbol,
                error=str(exc),
            )
            return RealtimeQuote(
                symbol=symbol,
                name="--",
                market=market,
                price=Decimal("0"),
                change=Decimal("0"),
                pct_change=Decimal("0"),
                volume=Decimal("0"),
                amount=Decimal("0"),
                timestamp=datetime.now().astimezone(),
                source=StockProviderName.EASTMONEY,
            )

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

        When all providers fail, returns an empty list so the
        frontend displays "--" for chart data.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            start_date: Optional start date.
            end_date: Optional end date.
            adjust: Price adjustment mode.

        Returns:
            Kline bars or empty list.
        """
        cache_key = f"kline:{market}:{symbol}:{start_date}:{end_date}:{adjust}"
        cached = await redis_cache.get_json(cache_key)
        if isinstance(cached, list):
            try:
                return [KlineBar.model_validate(item) for item in cached]
            except Exception:
                pass
        try:
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
        except (StockException, Exception) as exc:
            logger.warning(
                "Daily Kline unavailable: symbol={symbol} error={error}",
                symbol=symbol,
                error=str(exc),
            )
            return []

    async def get_financial_indicators(self, symbol: str) -> FinancialIndicators:
        """
        Fetch financial and valuation indicators from East Money.

        When the provider fails, returns a FinancialIndicators with
        symbol, name="--", and all values set to None so the frontend
        displays "--".

        Args:
            symbol: Stock symbol.

        Returns:
            Financial indicator response or fallback placeholder.
        """
        cache_key = f"financials:A:{symbol}"
        cached = await redis_cache.get_json(cache_key)
        if isinstance(cached, dict):
            try:
                return FinancialIndicators.model_validate(cached)
            except Exception:
                pass
        try:
            provider = EastMoneyStockProvider()
            try:
                indicators = await provider.get_financial_indicators(symbol)
            finally:
                await provider.close()
            await redis_cache.set_json(
                cache_key,
                indicators.model_dump(mode="json"),
                ttl_seconds=settings.finance_cache_ttl_seconds,
            )
            return indicators
        except (StockException, Exception) as exc:
            logger.warning(
                "Financial indicators unavailable: symbol={symbol} error={error}",
                symbol=symbol,
                error=str(exc),
            )
            return FinancialIndicators(symbol=symbol, name="--")


stock_service = StockService()
