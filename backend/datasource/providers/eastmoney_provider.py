"""
East Money (东方财富) real stock data provider.
No API key needed. Fetches data via East Money public HTTPS API.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Literal

import httpx

from backend.datasource.providers.base import (
    KlineBar,
    Market,
    RealtimeQuote,
    StockIdentity,
    StockProvider,
)
from backend.core.config.settings import StockProviderName

logger = logging.getLogger(__name__)

# secid prefix: 0=SZSE, 1=SSE, 2=BJSE
def _secid(symbol: str) -> str:
    if symbol.startswith("6") or symbol.startswith("9"): return f"1.{symbol}"
    if symbol.startswith("4") or symbol.startswith("8"): return f"2.{symbol}"
    return f"0.{symbol}"

def _exchange(symbol: str) -> str:
    if symbol.startswith("6") or symbol.startswith("9"): return "SSE"
    if symbol.startswith("4") or symbol.startswith("8"): return "BJSE"
    return "SZSE"

# East Money quote field mapping
EM_QUOTE_FIELDS = 'f43,f44,f45,f46,f47,f48,f169,f170,f57,f58,f86,f100,f116,f117,f168'
# f43=最新价 f44=最高 f45=最低 f46=开盘 f47=成交量 f48=成交额 f169=涨跌额 f170=涨跌幅
# f57=股票代码 f58=股票名称 f86=市盈率 f100=换手率 f116=总市值 f117=流通市值 f168=振幅

EM_STOCK_LIST_URL = 'https://push2.eastmoney.com/api/qt/clist/get'
EM_QUOTE_URL = 'https://push2.eastmoney.com/api/qt/stock/get'
EM_KLINE_URL = 'https://push2.eastmoney.com/api/qt/stock/kline/get'


class EastMoneyStockProvider(StockProvider):
    """Stock data provider using East Money public HTTPS API."""

    provider_name = StockProviderName.EASTMONEY

    def __init__(self) -> None:
        self._http = httpx.AsyncClient(timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        self._stock_cache: dict[str, StockIdentity] | None = None

    async def search_stocks(self, keyword: str, market: Market = 'A') -> list[StockIdentity]:
        if not self._stock_cache:
            await self._load_stock_list()
        if not self._stock_cache:
            return []
        kw = keyword.lower()
        result = []
        for s in self._stock_cache.values():
            if kw in s.symbol.lower() or kw in s.name.lower():
                result.append(s)
                if len(result) >= 50:
                    break
        return result

    async def _load_stock_list(self) -> None:
        try:
            params = {'pn': 1, 'pz': 6000, 'po': 1, 'np': 1, 'fltt': 2, 'invt': 2,
                      'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23', 'fields': 'f12,f14,f20' }
            resp = await self._http.get(EM_STOCK_LIST_URL, params=params)
            data = resp.json()
            items = (data.get('data') or {}).get('diff') or []
            cache = {}
            for item in items:
                code = str(item.get('f12', '')).strip()
                name = str(item.get('f14', '')).strip()
                if not code or not name:
                    continue
                ind = {6: '银行', 7: '房地产', 8: '综合', 9: '建筑材料', 10: '建筑装饰', 11: '建筑装饰', 12: '房地产', 13: '房地产', 14: '房地产', 15: '房地产'}
                cache[code] = StockIdentity(
                    symbol=code, name=name, market='A',
                    exchange=_exchange(code), industry=''
                )
            self._stock_cache = cache
            logger.info("Loaded %d stocks from East Money", len(cache))
        except Exception as e:
            logger.warning("Failed to load stock list from East Money: %s", e)
            self._stock_cache = {}

    async def get_realtime_quote(self, symbol: str, market: Market = 'A') -> RealtimeQuote:
        params = {'secid': _secid(symbol), 'fields': EM_QUOTE_FIELDS}
        resp = await self._http.get(EM_QUOTE_URL, params=params)
        data = (resp.json()).get('data') or {}
        name = str(data.get('f58', symbol))
        price = self._d(data.get('f43'))
        high = self._d(data.get('f44'))
        low = self._d(data.get('f45'))
        open_p = self._d(data.get('f46'))
        volume = self._d(data.get('f47'), 1)
        amount = self._d(data.get('f48'), 1)
        change = self._d(data.get('f169'))
        pct = self._d(data.get('f170'))
        return RealtimeQuote(
            symbol=symbol, name=name, market=market,
            price=price, change=change, pct_change=pct,
            volume=volume, amount=amount,
            timestamp=datetime.now().astimezone(),
            source=StockProviderName.EASTMONEY,
        )

    async def get_daily_kline(
        self, symbol: str, market: Market = 'A',
        start_date: date | None = None, end_date: date | None = None,
        adjust: Literal['none', 'qfq', 'hfq'] = 'qfq',
    ) -> list[KlineBar]:
        end = end_date or datetime.now().date()
        start = start_date or (end - timedelta(days=365))
        fqt = 0 if adjust == 'none' else (1 if adjust == 'qfq' else 2)
        params = {'secid': _secid(symbol), 'klt': 101, 'fqt': fqt,
                  'beg': start.strftime('%Y%m%d'), 'end': end.strftime('%Y%m%d')}
        resp = await self._http.get(EM_KLINE_URL, params=params)
        raw = (resp.json()).get('data') or {}
        klines = raw.get('klines') or []
        bars = []
        for line in klines:
            parts = line.split(',')
            if len(parts) < 7: continue
            d = parts[0].replace('-', '')
            try:
                bars.append(KlineBar(
                    symbol=symbol, market=market,
                    trade_date=datetime.strptime(d, '%Y%m%d').date(),
                    open_price=Decimal(str(parts[1])),
                    close_price=Decimal(str(parts[2])),
                    high_price=Decimal(str(parts[3])),
                    low_price=Decimal(str(parts[4])),
                    volume=Decimal(str(int(float(parts[5])))),
                    amount=Decimal(str(int(float(parts[6])))),
                    source=StockProviderName.EASTMONEY,
                ))
            except (ValueError, IndexError):
                continue
        return bars

    @staticmethod
    def _d(val, default=Decimal('0')) -> Decimal:
        if val is None: return default
        try: return Decimal(str(val))
        except: return default

    async def close(self) -> None:
        await self._http.aclose()