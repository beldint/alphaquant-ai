"""
Project: AlphaQuant AI
File: backend/datasource/providers/yahoo_provider.py
Description: Yahoo Finance stock data provider.
Python Version: 3.11.9
"""

from __future__ import annotations
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Literal
from backend.datasource.providers.base import (
    KlineBar,
    Market,
    RealtimeQuote,
    StockIdentity,
    StockProvider,
)
import httpx
from backend.datasource.providers.http_client import build_async_client

YAHOO_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class YahooStockProvider(StockProvider):
    provider_name: str = "yahoo"

    async def search_stocks(
        self, keyword: str, market: Market = "A"
    ) -> list[StockIdentity]:
        return []

    async def get_realtime_quote(
        self, symbol: str, market: Market = "A"
    ) -> RealtimeQuote:
        sym = _to_yahoo_symbol(symbol, market)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
        async with build_async_client(
            timeout=15, headers={"User-Agent": YAHOO_UA}
        ) as client:
            resp = await client.get(url, headers={"User-Agent": YAHOO_UA})
            data = resp.json()
        result = data.get("chart", {}).get("result", [{}])[0]
        meta = result.get("meta", {})
        quotes = result.get("indicators", {}).get("quote", [{}])[0]
        reg = meta.get("regularMarketPrice", 0)
        prev = meta.get("chartPreviousClose", reg)
        change = reg - prev
        pct = (change / prev * 100) if prev else 0
        vol = (
            (quotes.get("volume") or [0])[-1]
            if isinstance(quotes.get("volume"), list)
            else 0
        )
        return RealtimeQuote(
            symbol=symbol,
            name=meta.get("symbol", symbol),
            market=market,
            price=Decimal(str(reg)),
            change=Decimal(str(change)),
            pct_change=Decimal(str(round(pct, 2))),
            volume=Decimal(str(vol)),
            amount=Decimal(str(vol * reg)),
            timestamp=datetime.now(timezone.utc),
            source="yahoo",
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
        sym = _to_yahoo_symbol(symbol, market)
        end = end_date or date.today()
        start = start_date or (end - timedelta(days=365))
        days = (end - start).days
        rng = (
            "6mo"
            if days <= 180
            else (
                "1y"
                if days <= 365
                else "2y" if days <= 730 else "5y" if days <= 1825 else "max"
            )
        )
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval=1d"
        async with build_async_client(
            timeout=15, headers={"User-Agent": YAHOO_UA}
        ) as client:
            resp = await client.get(url, headers={"User-Agent": YAHOO_UA})
            data = resp.json()
        result = data.get("chart", {}).get("result", [{}])[0]
        timestamps = result.get("timestamp", [])
        quotes = result.get("indicators", {}).get("quote", [{}])[0]
        opens = quotes.get("open", []) or []
        highs = quotes.get("high", []) or []
        lows = quotes.get("low", []) or []
        closes = quotes.get("close", []) or []
        volumes = quotes.get("volume", []) or []
        bars = []
        for i in range(len(timestamps)):
            if i < len(opens) and opens[i] is not None:
                td = datetime.fromtimestamp(timestamps[i], tz=timezone.utc).date()
                o, h, l, c, v = opens[i], highs[i], lows[i], closes[i], volumes[i] or 0
                v = v if v else 0
                bars.append(
                    KlineBar(
                        symbol=symbol,
                        market=market,
                        trade_date=td,
                        open_price=Decimal(str(o)),
                        high_price=Decimal(str(h)),
                        low_price=Decimal(str(l)),
                        close_price=Decimal(str(c)),
                        volume=Decimal(str(v)),
                        amount=Decimal(str(v * c)),
                        source="yahoo",
                    )
                )
        return bars


def _to_yahoo_symbol(symbol: str, market: Market) -> str:
    if market == "A":
        return f"{symbol}.SS" if symbol.startswith(("5", "6", "9")) else f"{symbol}.SZ"
    elif market == "HK":
        return f"{symbol}.HK"
    return symbol
