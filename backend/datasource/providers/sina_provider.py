"""
Project: AlphaQuant AI
File: backend/datasource/providers/sina_provider.py
Description: Sina Finance backup realtime quote provider for A-share stocks.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Literal

from loguru import logger

from backend.core.config import settings
from backend.core.config.settings import StockProviderName
from backend.core.exceptions import StockException
from backend.datasource.providers.base import (
    KlineBar,
    Market,
    RealtimeQuote,
    StockIdentity,
    StockProvider,
)
from backend.datasource.providers.http_client import build_async_client
from backend.datasource.providers.stock_code import (
    infer_exchange,
    normalize_symbol,
    prefixed_symbol,
)

SINA_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class SinaStockProvider(StockProvider):
    """Stock data provider using Sina Finance public realtime quote API."""

    provider_name = StockProviderName.SINA

    def __init__(self) -> None:
        """Initialize reusable HTTP client."""
        self._http = build_async_client(
            timeout=settings.stock_request_timeout_seconds,
            headers={
                "User-Agent": SINA_USER_AGENT,
                "Referer": "https://finance.sina.com.cn/",
            },
        )

    async def search_stocks(
        self,
        keyword: str,
        market: Market = "A",
    ) -> list[StockIdentity]:
        """
        Resolve direct six-digit symbol lookups through Sina realtime quote.

        Args:
            keyword: Stock symbol keyword.
            market: Market identifier.

        Returns:
            One identity for exact symbols, otherwise an empty list.
        """
        if market != "A":
            raise StockException(
                "Sina provider currently supports A-share data",
                provider=self.provider_name.value,
            )
        try:
            symbol = normalize_symbol(keyword)
        except StockException:
            return []
        quote = await self.get_realtime_quote(symbol, market)
        return [
            StockIdentity(
                symbol=symbol,
                name=quote.name,
                market="A",
                exchange=infer_exchange(symbol),
            ),
        ]

    async def get_realtime_quote(
        self,
        symbol: str,
        market: Market = "A",
    ) -> RealtimeQuote:
        """
        Fetch a realtime A-share quote from Sina Finance.

        Args:
            symbol: Stock symbol.
            market: Market identifier.

        Returns:
            Unified realtime quote.
        """
        if market != "A":
            raise StockException(
                "Sina provider currently supports A-share quotes",
                provider=self.provider_name.value,
            )
        code = normalize_symbol(symbol)
        query_symbol = prefixed_symbol(code)
        url = f"{str(settings.sina_base_url).rstrip('/')}/list={query_symbol}"
        try:
            response = await self._http.get(str(url))
            response.raise_for_status()
            fields = _parse_sina_payload(response.text, query_symbol)
            current = _decimal_at(fields, 3)
            previous_close = _decimal_at(fields, 2)
            change = current - previous_close
            pct_change = (
                Decimal("0")
                if previous_close == 0
                else (change / previous_close * Decimal("100")).quantize(
                    Decimal("0.01")
                )
            )
            volume = _decimal_at(fields, 8)
            amount = _decimal_at(fields, 9)
            if current <= 0:
                raise StockException(
                    "Sina quote price is empty",
                    provider=self.provider_name.value,
                    symbol=code,
                )
            return RealtimeQuote(
                symbol=code,
                name=_string_at(fields, 0, code),
                market="A",
                price=current,
                change=change,
                pct_change=pct_change,
                volume=volume,
                amount=amount,
                timestamp=_parse_sina_time(
                    _string_at(fields, 30, ""), _string_at(fields, 31, "")
                ),
                source=self.provider_name,
            )
        except StockException:
            raise
        except Exception as exc:
            logger.exception("Sina realtime quote failed: symbol={symbol}", symbol=code)
            raise StockException(
                "Sina realtime quote failed",
                provider=self.provider_name.value,
                symbol=code,
                cause=exc,
            ) from exc

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
        Sina is used as realtime quote backup; historical Kline falls through.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            start_date: Optional start date.
            end_date: Optional end date.
            adjust: Price adjustment mode.

        Raises:
            StockException: Always, so manager can use the next Kline provider.
        """
        raise StockException(
            "Sina Kline provider is not configured",
            provider=self.provider_name.value,
            symbol=symbol,
        )

    async def close(self) -> None:
        """Close HTTP resources."""
        await self._http.aclose()


def _parse_sina_payload(text: str, query_symbol: str) -> list[str]:
    marker = f'var hq_str_{query_symbol}="'
    if marker not in text:
        raise StockException(
            "Sina quote payload is invalid", details={"payload": text[:120]}
        )
    body = text.split(marker, 1)[1].split('";', 1)[0]
    fields = body.split(",")
    if len(fields) < 32 or not fields[0]:
        raise StockException("Sina quote payload has insufficient fields")
    return fields


def _string_at(fields: list[str], index: int, default: str) -> str:
    try:
        value = fields[index].strip()
    except IndexError:
        return default
    return value or default


def _decimal_at(fields: list[str], index: int) -> Decimal:
    try:
        raw = fields[index].strip()
        return Decimal(raw or "0")
    except (IndexError, InvalidOperation):
        return Decimal("0")


def _parse_sina_time(day: str, clock: str) -> datetime:
    try:
        return datetime.strptime(f"{day} {clock}", "%Y-%m-%d %H:%M:%S").astimezone()
    except ValueError:
        return datetime.now().astimezone()
