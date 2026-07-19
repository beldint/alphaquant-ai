"""
Project: AlphaQuant AI
File: backend/datasource/providers/eastmoney_provider.py
Description: East Money provider for A-share Kline, valuation, and capital data.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Literal

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
    eastmoney_secid,
    infer_exchange,
    normalize_symbol,
)
from backend.schemas.financial import FinancialIndicators

MARKET_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

EASTMONEY_QUOTE_FIELDS = (
    "f43,f44,f45,f46,f47,f48,f57,f58,f86,f100,f116,f117,f162,f167,f168,f169,f170"
)


class EastMoneyStockProvider(StockProvider):
    """Stock data provider using East Money public HTTPS APIs."""

    provider_name = StockProviderName.EASTMONEY

    def __init__(self) -> None:
        """Initialize reusable HTTP client and stock-list cache."""
        self._http = build_async_client(
            timeout=settings.stock_request_timeout_seconds,
            headers={
                "User-Agent": MARKET_USER_AGENT,
                "Referer": "https://quote.eastmoney.com/",
            },
        )
        self._stock_cache: dict[str, StockIdentity] | None = None

    async def search_stocks(
        self,
        keyword: str,
        market: Market = "A",
    ) -> list[StockIdentity]:
        """
        Search A-share stock identities through East Money.

        Args:
            keyword: Stock code or name keyword.
            market: Market identifier.

        Returns:
            Matched stock identities.
        """
        if market != "A":
            raise StockException(
                "East Money provider currently supports A-share search",
                provider=self.provider_name.value,
            )
        if self._stock_cache is None:
            await self._load_stock_list()
        if not self._stock_cache:
            return []
        normalized_keyword = keyword.strip().lower()
        matches = [
            stock
            for stock in self._stock_cache.values()
            if normalized_keyword in stock.symbol.lower()
            or normalized_keyword in stock.name.lower()
        ]
        return matches[:50]

    async def get_realtime_quote(
        self,
        symbol: str,
        market: Market = "A",
    ) -> RealtimeQuote:
        """
        Fetch realtime A-share quote from East Money.

        Args:
            symbol: Stock symbol.
            market: Market identifier.

        Returns:
            Unified realtime quote.
        """
        if market != "A":
            raise StockException(
                "East Money provider currently supports A-share quotes",
                provider=self.provider_name.value,
            )
        code = normalize_symbol(symbol)
        data = await self._get_quote_data(code)
        price = _scaled_decimal(data.get("f43"))
        if price is None or price <= 0:
            raise StockException(
                "East Money quote price is empty",
                provider=self.provider_name.value,
                symbol=code,
            )
        return RealtimeQuote(
            symbol=code,
            name=str(data.get("f58") or code),
            market="A",
            price=price,
            change=_scaled_decimal(data.get("f169")),
            pct_change=_scaled_decimal(data.get("f170")),
            volume=_decimal(data.get("f47")),
            amount=_decimal(data.get("f48")),
            timestamp=datetime.now().astimezone(),
            source=self.provider_name,
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
        Fetch daily A-share Kline data from East Money.

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
                "East Money provider currently supports A-share Kline",
                provider=self.provider_name.value,
            )
        code = normalize_symbol(symbol)
        end = end_date or date.today()
        start = start_date or (end - timedelta(days=365))
        fqt = 0 if adjust == "none" else 1 if adjust == "qfq" else 2
        url = f"{str(settings.eastmoney_base_url).rstrip('/')}/api/qt/stock/kline/get"
        params = {
            "secid": eastmoney_secid(code),
            "klt": 101,
            "fqt": fqt,
            "beg": start.strftime("%Y%m%d"),
            "end": end.strftime("%Y%m%d"),
        }
        try:
            response = await self._http.get(str(url), params=params)
            response.raise_for_status()
            payload = response.json()
            rows = ((payload.get("data") or {}).get("klines")) or []
            bars = [_to_kline_bar(code, row, self.provider_name) for row in rows]
            return [bar for bar in bars if bar is not None]
        except Exception as exc:
            logger.exception(
                "East Money daily Kline failed: symbol={symbol}", symbol=code
            )
            raise StockException(
                "East Money daily Kline failed",
                provider=self.provider_name.value,
                symbol=code,
                cause=exc,
            ) from exc

    async def get_financial_indicators(self, symbol: str) -> FinancialIndicators:
        """
        Fetch valuation, capital, and financial indicators from East Money.

        Args:
            symbol: Six-digit A-share symbol.

        Returns:
            Unified financial indicator schema.
        """
        code = normalize_symbol(symbol)
        # Quote data from push2 endpoint may be unavailable (server drops connections).
        # Financial data from datacenter API still works, so we gracefully degrade
        # by returning None for quote-derived fields (PE/PB/market_cap).
        quote_data: dict[str, Any] = {}
        try:
            quote_data = await self._get_quote_data(code)
        except Exception as exc:
            logger.debug(
                "East Money quote data unavailable for financials (will use fallback): "
                "symbol={symbol} error={error}",
                symbol=code,
                error=str(exc),
            )
        financial_data = await self._get_latest_financial_data(code)
        return FinancialIndicators(
            symbol=code,
            name=str(quote_data.get("f58") or code),
            report_date=_string_or_none(financial_data.get("REPORT_DATE")),
            net_profit=_float_or_none(financial_data.get("PARENTNETPROFIT")),
            deducted_net_profit=_float_or_none(
                financial_data.get("KCFJCXSYJLR")
            ),
            gross_margin=_float_or_none(financial_data.get("XSMLL")),
            net_margin=_float_or_none(financial_data.get("XSJLL")),
            roe=_float_or_none(financial_data.get("ROEJQ")),
            revenue=_float_or_none(financial_data.get("TOTALOPERATEREVE")),
            revenue_growth=_float_or_none(financial_data.get("TOTALOPERATEREVETZ")),
            debt_ratio=_float_or_none(financial_data.get("ZCFZL")),
            current_ratio=_float_or_none(financial_data.get("LD")),
            quick_ratio=_float_or_none(financial_data.get("SD")),
            operating_cashflow=_float_or_none(financial_data.get("NETCASH_OPERATE_PK")),
            pe_ttm=_maybe_quote_pe(quote_data.get("f162")),
            pb=_maybe_quote_pb(quote_data.get("f167")),
            market_cap=_float_or_none(quote_data.get("f116")),
            total_shares=_float_or_none(
                financial_data.get("TOTAL_SHARE") or quote_data.get("f117")
            ),
        )

    async def close(self) -> None:
        """Close HTTP resources."""
        await self._http.aclose()

    async def _load_stock_list(self) -> None:
        url = f"{str(settings.eastmoney_base_url).rstrip('/')}/api/qt/clist/get"
        params = {
            "pn": 1,
            "pz": 6000,
            "po": 1,
            "np": 1,
            "fltt": 2,
            "invt": 2,
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81,m:1+t:3",
            "fields": "f12,f14,f100",
        }
        try:
            response = await self._http.get(str(url), params=params)
            response.raise_for_status()
            data = response.json()
            rows = ((data.get("data") or {}).get("diff")) or []
            self._stock_cache = {
                str(row.get("f12")).strip(): StockIdentity(
                    symbol=str(row.get("f12")).strip(),
                    name=str(row.get("f14")).strip(),
                    market="A",
                    exchange=infer_exchange(str(row.get("f12")).strip()),
                    industry=_string_or_none(row.get("f100")),
                )
                for row in rows
                if str(row.get("f12") or "").strip()
                and str(row.get("f14") or "").strip()
            }
            logger.info(
                "Loaded {count} stocks from East Money", count=len(self._stock_cache)
            )
        except Exception as exc:
            logger.warning(
                "Failed to load East Money stock list: {error}", error=str(exc)
            )
            self._stock_cache = {}

    async def _get_quote_data(self, symbol: str) -> dict[str, Any]:
        url = f"{str(settings.eastmoney_base_url).rstrip('/')}/api/qt/stock/get"
        params = {"secid": eastmoney_secid(symbol), "fields": EASTMONEY_QUOTE_FIELDS}
        try:
            response = await self._http.get(str(url), params=params)
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data") or {}
            if not data:
                raise StockException(
                    "East Money quote data is empty",
                    provider=self.provider_name.value,
                    symbol=symbol,
                )
            return data
        except StockException:
            raise
        except Exception as exc:
            logger.warning(
                "East Money quote request failed: symbol={symbol} error={error}",
                symbol=symbol,
                error=str(exc),
            )
            return {}

    async def _get_latest_financial_data(self, symbol: str) -> dict[str, Any]:
        url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
        params = {
            "reportName": "RPT_F10_FINANCE_MAINFINADATA",
            "columns": "ALL",
            "filter": f'(SECURITY_CODE="{symbol}")',
            "pageNumber": 1,
            "pageSize": 1,
            "sortTypes": -1,
            "sortColumns": "REPORT_DATE",
        }
        try:
            response = await self._http.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
            rows = ((payload.get("result") or {}).get("data")) or []
            return rows[0] if rows else {}
        except Exception as exc:
            logger.warning(
                "East Money financial API failed: symbol={symbol} error={error}",
                symbol=symbol,
                error=str(exc),
            )
            return {}


def _to_kline_bar(symbol: str, row: str, source: StockProviderName) -> KlineBar | None:
    parts = row.split(",")
    if len(parts) < 7:
        return None
    try:
        return KlineBar(
            symbol=symbol,
            market="A",
            trade_date=datetime.strptime(parts[0], "%Y-%m-%d").date(),
            open_price=Decimal(parts[1]),
            close_price=Decimal(parts[2]),
            high_price=Decimal(parts[3]),
            low_price=Decimal(parts[4]),
            volume=Decimal(parts[5]),
            amount=Decimal(parts[6]),
            source=source,
        )
    except (InvalidOperation, ValueError) as exc:
        logger.debug(
            "Skipped invalid East Money Kline row: row={row} error={error}",
            row=row,
            error=str(exc),
        )
        return None


def _decimal(value: object) -> Decimal:
    if value is None or value == "-":
        return Decimal("0")
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return Decimal("0")


def _scaled_decimal(value: object) -> Decimal:
    if value is None or value == "-":
        return Decimal("0")
    try:
        return Decimal(str(value)) / Decimal("100")
    except InvalidOperation:
        return Decimal("0")


def _maybe_quote_pe(value: object) -> float | None:
    """Return PE from quote data, scaled by 100, or None if unavailable."""
    if value is None or value == "-":
        return None
    try:
        scaled = float(str(value)) / 100.0
        return scaled if scaled > 0 else None
    except (TypeError, ValueError, InvalidOperation):
        return None


def _maybe_quote_pb(value: object) -> float | None:
    """Return PB from quote data, scaled by 100, or None if unavailable."""
    if value is None or value == "-":
        return None
    try:
        scaled = float(str(value)) / 100.0
        return scaled if scaled > 0 else None
    except (TypeError, ValueError, InvalidOperation):
        return None


def _float_or_none(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _string_or_none(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
