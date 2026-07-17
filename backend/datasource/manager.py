"""
Project: AlphaQuant AI
File: backend/datasource/manager.py
Description: Stock provider manager with priority failover and retry support.
Python Version: 3.11.9
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import date
from typing import Literal, TypeVar

from loguru import logger

from backend.core.config import Settings, settings
from backend.core.config.settings import StockProviderName
from backend.core.exceptions import ConfigurationException, StockException
from backend.datasource.providers.akshare_provider import AKShareProvider
from backend.datasource.providers.mock_provider import MockStockProvider
from backend.datasource.providers.eastmoney_provider import EastMoneyStockProvider
from backend.datasource.providers.eastmoney_provider import EastMoneyStockProvider
from backend.datasource.providers.base import (
    KlineBar,
    Market,
    RealtimeQuote,
    StockIdentity,
    StockProvider,
)


ResultT = TypeVar("ResultT")


class StockProviderManager:
    """Manage stock data providers with failover and retry behavior."""

    def __init__(self, app_settings: Settings) -> None:
        """
        Initialize provider manager.

        Args:
            app_settings: Application settings.
        """
        self.settings = app_settings
        self.providers = self._build_providers()

    async def search_stocks(
        self,
        keyword: str,
        market: Market = "A",
    ) -> list[StockIdentity]:
        """
        Search stocks through prioritized providers.

        Args:
            keyword: Stock code or name keyword.
            market: Market identifier.

        Returns:
            Matched stock identities.
        """
        return await self._execute_with_failover(
            lambda provider: provider.search_stocks(keyword, market),
        )

    async def get_realtime_quote(
        self,
        symbol: str,
        market: Market = "A",
    ) -> RealtimeQuote:
        """
        Fetch realtime quote through prioritized providers.

        Args:
            symbol: Stock symbol.
            market: Market identifier.

        Returns:
            Unified realtime quote.
        """
        return await self._execute_with_failover(
            lambda provider: provider.get_realtime_quote(symbol, market),
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
        Fetch daily Kline data through prioritized providers.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            start_date: Optional start date.
            end_date: Optional end date.
            adjust: Price adjustment mode.

        Returns:
            Unified Kline bars.
        """
        return await self._execute_with_failover(
            lambda provider: provider.get_daily_kline(
                symbol,
                market=market,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust,
            ),
        )

    async def close(self) -> None:
        """Close all provider resources."""
        for provider in self.providers.values():
            await provider.close()

    def _build_providers(self) -> dict[StockProviderName, StockProvider]:
        """
        Build configured stock providers.

        Returns:
            Provider map.
        """
        return {
            StockProviderName.EASTMONEY: EastMoneyStockProvider(),
            StockProviderName.TUSHARE: MockStockProvider(),
        }

    async def _execute_with_failover(
        self,
        operation: Callable[[StockProvider], Awaitable[ResultT]],
    ) -> ResultT:
        """
        Execute an operation against providers in configured priority order.

        Args:
            operation: Provider operation callback.

        Returns:
            Operation result.

        Raises:
            StockException: If all configured providers fail.
        """
        errors: list[str] = []
        for provider_name in self.settings.stock_provider_priority:
            provider = self.providers.get(provider_name)
            if provider is None:
                errors.append(f"{provider_name.value}: provider is not registered")
                continue
            try:
                return await self._retry_provider_operation(provider, operation)
            except StockException as exc:
                logger.warning(
                    "Stock provider failed: provider={provider} error={error}",
                    provider=provider_name.value,
                    error=exc.message,
                )
                errors.append(f"{provider_name.value}: {exc.message}")
        raise StockException(
            "All stock providers failed",
            details={"errors": errors},
        )

    async def _retry_provider_operation(
        self,
        provider: StockProvider,
        operation: Callable[[StockProvider], Awaitable[ResultT]],
    ) -> ResultT:
        """
        Execute provider operation with retry backoff.

        Args:
            provider: Stock data provider.
            operation: Provider operation callback.

        Returns:
            Operation result.
        """
        last_error: StockException | None = None
        attempts = self.settings.stock_max_retries + 1
        for attempt in range(1, attempts + 1):
            try:
                return await operation(provider)
            except StockException as exc:
                last_error = exc
                if attempt >= attempts:
                    break
                await asyncio.sleep(self.settings.stock_retry_backoff_seconds * attempt)
        if last_error is not None:
            raise last_error
        raise ConfigurationException("Stock provider retry configuration is invalid")


stock_provider_manager = StockProviderManager(settings)

