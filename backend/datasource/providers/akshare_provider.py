"""
Project: AlphaQuant AI
File: backend/datasource/providers/akshare_provider.py
Description: AKShare stock data provider implementation.
Python Version: 3.11.9
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from loguru import logger

from backend.core.config.settings import StockProviderName
from backend.core.exceptions import StockException
from backend.datasource.providers.base import (
    KlineBar,
    Market,
    RealtimeQuote,
    StockIdentity,
    StockProvider,
)


class AKShareProvider(StockProvider):
    """AKShare provider for A-share market data."""

    provider_name = StockProviderName.AKSHARE

    async def search_stocks(self, keyword: str, market: Market = "A") -> list[StockIdentity]:
        """
        Search A-share stocks through AKShare.

        Args:
            keyword: Stock code or name keyword.
            market: Market identifier.

        Returns:
            Matched stock identities.
        """
        if market != "A":
            raise StockException("AKShare provider currently supports A-share search", provider=self.provider_name.value)
        try:
            import akshare as ak

            frame = await asyncio.to_thread(ak.stock_info_a_code_name)
            matches = frame[
                frame["code"].astype(str).str.contains(keyword, case=False)
                | frame["name"].astype(str).str.contains(keyword, case=False)
            ]
            return [
                StockIdentity(
                    symbol=str(row["code"]),
                    name=str(row["name"]),
                    market="A",
                    exchange=_infer_a_share_exchange(str(row["code"])),
                )
                for _, row in matches.head(50).iterrows()
            ]
        except Exception as exc:
            logger.exception("AKShare stock search failed: keyword={keyword}", keyword=keyword)
            raise StockException(
                "AKShare stock search failed",
                provider=self.provider_name.value,
                details={"keyword": keyword},
                cause=exc,
            ) from exc

    async def get_realtime_quote(self, symbol: str, market: Market = "A") -> RealtimeQuote:
        """
        Fetch realtime A-share quote through AKShare.

        Args:
            symbol: Stock symbol.
            market: Market identifier.

        Returns:
            Unified realtime quote.
        """
        if market != "A":
            raise StockException("AKShare provider currently supports A-share quotes", provider=self.provider_name.value)
        try:
            import akshare as ak

            frame = await asyncio.to_thread(ak.stock_zh_a_spot_em)
            matched = frame[frame["代码"].astype(str) == symbol]
            if matched.empty:
                raise StockException(
                    "Stock quote not found",
                    provider=self.provider_name.value,
                    symbol=symbol,
                )
            row = matched.iloc[0]
            return RealtimeQuote(
                symbol=symbol,
                name=str(row["名称"]),
                market="A",
                price=Decimal(str(row["最新价"])),
                change=Decimal(str(row["涨跌额"])),
                pct_change=Decimal(str(row["涨跌幅"])),
                volume=Decimal(str(row["成交量"])),
                amount=Decimal(str(row["成交额"])),
                timestamp=datetime.now().astimezone(),
                source=self.provider_name,
            )
        except StockException:
            raise
        except Exception as exc:
            logger.exception("AKShare realtime quote failed: symbol={symbol}", symbol=symbol)
            raise StockException(
                "AKShare realtime quote failed",
                provider=self.provider_name.value,
                symbol=symbol,
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
        Fetch daily A-share Kline data through AKShare.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            start_date: Optional start date.
            end_date: Optional end date.
            adjust: Price adjustment mode.

        Returns:
            Unified Kline bars.
        """
        if market != "A":
            raise StockException("AKShare provider currently supports A-share Kline", provider=self.provider_name.value)
        try:
            import akshare as ak

            start = start_date.strftime("%Y%m%d") if start_date else "19900101"
            end = end_date.strftime("%Y%m%d") if end_date else date.today().strftime("%Y%m%d")
            ak_adjust = "" if adjust == "none" else adjust
            frame = await asyncio.to_thread(
                ak.stock_zh_a_hist,
                symbol=symbol,
                period="daily",
                start_date=start,
                end_date=end,
                adjust=ak_adjust,
            )
            return [
                KlineBar(
                    symbol=symbol,
                    market="A",
                    trade_date=row["日期"],
                    open_price=Decimal(str(row["开盘"])),
                    high_price=Decimal(str(row["最高"])),
                    low_price=Decimal(str(row["最低"])),
                    close_price=Decimal(str(row["收盘"])),
                    volume=Decimal(str(row["成交量"])),
                    amount=Decimal(str(row["成交额"])),
                    source=self.provider_name,
                )
                for _, row in frame.iterrows()
            ]
        except Exception as exc:
            logger.exception("AKShare daily Kline failed: symbol={symbol}", symbol=symbol)
            raise StockException(
                "AKShare daily Kline failed",
                provider=self.provider_name.value,
                symbol=symbol,
                cause=exc,
            ) from exc


def _infer_a_share_exchange(symbol: str) -> str:
    """
    Infer A-share exchange from stock code prefix.

    Args:
        symbol: A-share stock code.

    Returns:
        Exchange code.
    """
    if symbol.startswith(("6", "9")):
        return "SSE"
    if symbol.startswith(("0", "2", "3")):
        return "SZSE"
    if symbol.startswith(("4", "8")):
        return "BSE"
    return "UNKNOWN"

