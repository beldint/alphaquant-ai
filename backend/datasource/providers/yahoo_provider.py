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
from loguru import logger
from backend.datasource.providers.http_client import build_async_client

YAHOO_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class YahooStockProvider(StockProvider):
    provider_name: str = "yahoo"

    async def search_stocks(
        self, keyword: str, market: Market = "A"
    ) -> list[StockIdentity]:
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        params = {"q": keyword, "quotesCount": 10}
        results = []
        try:
            async with build_async_client(
                timeout=10, headers={"User-Agent": YAHOO_UA}
            ) as client:
                # First try: original keyword
                resp = await client.get(url, params=params, headers={"User-Agent": YAHOO_UA})
                all_quotes = []
                if resp.status_code == 200:
                    data = resp.json()
                    all_quotes = data.get("quotes", []) or []
                    if not all_quotes:
                        rs = data.get("ResultSet")
                        if isinstance(rs, dict):
                            all_quotes = rs.get("Result", []) or []
                # Second try: with .HK suffix for HK stocks
                if not all_quotes and market == "HK" and keyword.isdigit():
                    hk_params = dict(params)
                    hk_params["q"] = keyword + ".HK"
                    hk_resp = await client.get(url, params=hk_params, headers={"User-Agent": YAHOO_UA})
                    if hk_resp.status_code == 200:
                        hk_data = hk_resp.json()
                        all_quotes = hk_data.get("quotes", []) or []
                        if not all_quotes:
                            rs = hk_data.get("ResultSet")
                            if isinstance(rs, dict):
                                all_quotes = rs.get("Result", []) or []
        except Exception as e:
            logger.warning("Yahoo search failed: {} keyword={}", e, keyword)
            return []
        logger.debug("Yahoo search: keyword={} total_quotes={}", keyword, len(all_quotes))
        for q in all_quotes:
            sym = str(q.get("symbol", ""))
            if not sym:
                continue
            name = str(q.get("shortname") or q.get("longname") or sym)
            # Strip exchange suffix from display name if name is just the symbol
            if name == sym:
                for sep in (".HK", ".TW", ".SS", ".SZ", ".TO", ".L", ".DE"):
                    if sym.endswith(sep):
                        name = sym[:len(sym)-len(sep)]
                        break
            exch = str(q.get("exchange", "") or "")
            if market == "US":
                # For US market, exclude non-US suffixes and options/derivatives
                non_us_suffixes = (".HK", ".TW", ".SS", ".SZ", ".TO", ".V", ".L", ".DE", ".PA", ".BR", ".MI", ".MC",
                    ".SN", ".HE", ".ST", ".CO", ".IR", ".VI", ".AS", ".NX", ".BO", ".NS", ".KS", ".KQ",
                    ".T", ".N", ".SW", ".BA", ".BK", ".MX", ".OL", ".SG", ".TA")
                # Also exclude options/derivatives (symbols with 6+ consecutive digits)
                has_date_pattern = bool(re.search(r"\d{6,}", sym))
                if not any(sym.endswith(s) for s in non_us_suffixes) and not has_date_pattern:
                    results.append(StockIdentity(
                        symbol=sym, name=name, market="US",
                        exchange="NASDAQ" if exch in ("NMS","NGM","NCM") else "NYSE",
                        industry=q.get("sector"),
                    ))
            elif market == "HK":
                # For HK market, include .HK symbols or HKG/SEHK exchange stocks
                if sym.endswith(".HK"):
                    code = sym[:-3]
                elif exch in ("HKG", "SEHK") or q.get("market", "") == "hk_market":
                    code = sym.replace(".HK", "")
                    name = str(q.get("shortname") or q.get("longname") or code)
                else:
                    continue
                results.append(StockIdentity(
                    symbol=code, name=name, market="HK",
                    exchange="HKEX", industry=q.get("sector"),
                ))
            elif market == "A":
                if sym.endswith((".SS", ".SZ")):
                    code = sym[:-3]
                    exch2 = "SSE" if sym.endswith(".SS") else "SZSE"
                    results.append(StockIdentity(
                        symbol=code, name=name, market="A",
                        exchange=exch2, industry=q.get("sector"),
                    ))
        # Fallback: try direct quote lookup for exact code match
        if not results and keyword.strip():
            try:
                qsym = _to_yahoo_symbol(keyword, market)
                qurl = f"https://query1.finance.yahoo.com/v8/finance/chart/{qsym}"
                async with build_async_client(
                    timeout=10, headers={"User-Agent": YAHOO_UA}
                ) as qclient:
                    qresp = await qclient.get(qurl, headers={"User-Agent": YAHOO_UA})
                    if qresp.status_code == 200:
                        qdata = qresp.json()
                        qresult = (qdata.get("chart") or {}).get("result", [{}])[0]
                        qmeta = qresult.get("meta", {})
                        qname = str(qmeta.get("symbol", "") or keyword)
                        if qname:
                            results.append(StockIdentity(
                                symbol=keyword, name=qname, market=market,
                                exchange="YAHOO", industry=None,
                            ))
            except Exception:
                pass
        return results

    async def get_realtime_quote(
        self, symbol: str, market: Market = "A"
    ) -> RealtimeQuote:
        sym = _to_yahoo_symbol(symbol, market)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
        try:
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
        except Exception as e:
            raise StockException(
                "Yahoo quote failed",
                provider=self.provider_name,
                cause=e,
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
        try:
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
        except Exception as e:
            raise StockException(
                "Yahoo daily Kline failed",
                provider=self.provider_name,
                cause=e,
            )


def _to_yahoo_symbol(symbol: str, market: Market) -> str:
    if market == "A":
        return f"{symbol}.SS" if symbol.startswith(("5", "6", "9")) else f"{symbol}.SZ"
    elif market == "HK":
        return f"{symbol}.HK"
    return symbol

