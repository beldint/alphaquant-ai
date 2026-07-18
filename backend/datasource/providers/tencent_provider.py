"""
Project: AlphaQuant AI
File: backend/datasource/providers/tencent_provider.py
Description: Tencent Finance stock data provider for primary A-share quotes.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
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

TENCENT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " "AppleWebKit/537.36"
)


class TencentStockProvider(StockProvider):
    """Stock data provider using Tencent Finance public quote APIs."""

    provider_name = StockProviderName.TENCENT

    def __init__(self) -> None:
        """Initialize reusable HTTP client."""
        self._http = build_async_client(
            timeout=settings.stock_request_timeout_seconds,
            headers={
                "User-Agent": TENCENT_USER_AGENT,
                "Referer": "https://finance.qq.com/",
            },
        )

    async def search_stocks(
        self,
        keyword: str,
        market: Market = "A",
    ) -> list[StockIdentity]:
        """
        Resolve direct six-digit symbol lookups through Tencent realtime quote.

        Args:
            keyword: Stock symbol keyword.
            market: Market identifier.

        Returns:
            One identity for exact symbols, otherwise an empty list.
        """
        if market != "A":
            raise StockException(
                "Tencent provider currently supports A-share data",
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
        Fetch a realtime A-share quote from Tencent Finance.

        Args:
            symbol: Stock symbol.
            market: Market identifier.

        Returns:
            Unified realtime quote.
        """
        if market != "A":
            raise StockException(
                "Tencent provider currently supports A-share quotes",
                provider=self.provider_name.value,
            )
        code = normalize_symbol(symbol)
        query_symbol = prefixed_symbol(code)
        url = f"{str(settings.tencent_base_url).rstrip('/')}/q={query_symbol}"
        try:
            response = await self._http.get(str(url))
            response.raise_for_status()
            fields = _parse_tencent_payload(response.text, query_symbol)
            price = _decimal_at(fields, 3)
            previous_close = _decimal_at(fields, 4)
            change = _decimal_at(fields, 31, price - previous_close)
            pct_change = _decimal_at(fields, 32, _pct(change, previous_close))
            volume = _decimal_at(fields, 36, Decimal("0")) * Decimal("100")
            amount = _decimal_at(fields, 37, Decimal("0")) * Decimal("10000")
            if price <= 0:
                raise StockException(
                    "Tencent quote price is empty",
                    provider=self.provider_name.value,
                    symbol=code,
                )
            return RealtimeQuote(
                symbol=code,
                name=_string_at(fields, 1, code),
                market="A",
                price=price,
                change=change,
                pct_change=pct_change,
                volume=volume,
                amount=amount,
                timestamp=_parse_tencent_time(_string_at(fields, 30, "")),
                source=self.provider_name,
            )
        except StockException:
            raise
        except Exception as exc:
            logger.exception(
                "Tencent realtime quote failed: symbol={symbol}", symbol=code
            )
            raise StockException(
                "Tencent realtime quote failed",
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
        Fetch daily Kline bars from Tencent Finance.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            start_date: Optional start date.
            end_date: Optional end date.
            adjust: Price adjustment mode.

        Returns:
            Unified daily Kline bars.
        """
        if market != "A":
            raise StockException(
                "Tencent provider currently supports A-share Kline",
                provider=self.provider_name.value,
            )
        code = normalize_symbol(symbol)
        query_symbol = prefixed_symbol(code)
        end = end_date or date.today()
        start = start_date or (end - timedelta(days=365))
        count = max((end - start).days + 30, 120)
        fq_type = "qfq" if adjust == "qfq" else "hfq" if adjust == "hfq" else ""
        param = f"{query_symbol},day,,,{count},{fq_type}"
        url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
        try:
            response = await self._http.get(url, params={"param": param})
            response.raise_for_status()
            payload = response.json()
            symbol_data = (payload.get("data") or {}).get(query_symbol) or {}
            rows = (
                symbol_data.get("qfqday")
                or symbol_data.get("hfqday")
                or symbol_data.get("day")
                or []
            )
            bars = [
                _build_kline_bar(code, row, start, end, self.provider_name)
                for row in rows
            ]
            return [bar for bar in bars if bar is not None]
        except Exception as exc:
            logger.exception("Tencent daily Kline failed: symbol={symbol}", symbol=code)
            raise StockException(
                "Tencent daily Kline failed",
                provider=self.provider_name.value,
                symbol=code,
                cause=exc,
            ) from exc

    async def close(self) -> None:
        """Close HTTP resources."""
        await self._http.aclose()


def _parse_tencent_payload(text: str, query_symbol: str) -> list[str]:
    marker = f'v_{query_symbol}="'
    if marker not in text:
        raise StockException(
            "Tencent quote payload is invalid", details={"payload": text[:120]}
        )
    body = text.split(marker, 1)[1].split('";', 1)[0]
    fields = body.split("~")
    if len(fields) < 33:
        raise StockException("Tencent quote payload has insufficient fields")
    return fields


def _string_at(fields: list[str], index: int, default: str) -> str:
    try:
        value = fields[index].strip()
    except IndexError:
        return default
    return value or default


def _decimal_at(
    fields: list[str], index: int, default: Decimal | None = None
) -> Decimal:
    try:
        raw = fields[index].strip()
    except IndexError:
        return default if default is not None else Decimal("0")
    if not raw or raw == "--":
        return default if default is not None else Decimal("0")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return default if default is not None else Decimal("0")


def _pct(change: Decimal, previous_close: Decimal) -> Decimal:
    if previous_close == 0:
        return Decimal("0")
    return (change / previous_close * Decimal("100")).quantize(Decimal("0.01"))


def _parse_tencent_time(value: str) -> datetime:
    if len(value) >= 14 and value[:14].isdigit():
        return datetime.strptime(value[:14], "%Y%m%d%H%M%S").astimezone()
    return datetime.now().astimezone()


def _build_kline_bar(
    symbol: str,
    row: list[object],
    start_date: date,
    end_date: date,
    source: StockProviderName,
) -> KlineBar | None:
    if len(row) < 6:
        return None
    try:
        trade_date = datetime.strptime(str(row[0]), "%Y-%m-%d").date()
        if trade_date < start_date or trade_date > end_date:
            return None
        close_price = Decimal(str(row[2]))
        volume = Decimal(str(row[5]))
        return KlineBar(
            symbol=symbol,
            market="A",
            trade_date=trade_date,
            open_price=Decimal(str(row[1])),
            close_price=close_price,
            high_price=Decimal(str(row[3])),
            low_price=Decimal(str(row[4])),
            volume=volume,
            amount=Decimal("0"),
            source=source,
        )
    except (InvalidOperation, ValueError, TypeError) as exc:
        logger.debug(
            "Skipped invalid Tencent Kline row: row={row} error={error}",
            row=row,
            error=str(exc),
        )
        return None
