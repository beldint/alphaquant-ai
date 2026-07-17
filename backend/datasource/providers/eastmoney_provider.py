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
        self._http = httpx.AsyncClient(timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
        self._http2 = httpx.AsyncClient(timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
        self._stock_cache: dict[str, StockIdentity] | None = None
        self._proxy_available = True

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
                      'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23', 'fields': 'f12,f14' }
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
                    exchange=_exchange(code), industry=str(item.get('f20', ''))
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
        price = self._p(data.get('f43'))
        high = self._p(data.get('f44'))
        low = self._p(data.get('f45'))
        open_p = self._p(data.get('f46'))
        volume = self._v(data.get('f47'), Decimal('1'))
        amount = self._v(data.get('f48'), Decimal('1'))
        change = self._p(data.get('f169'))
        pct = self._p(data.get('f170'))
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
    def _p(val, default=Decimal('0')) -> Decimal:
        if val is None: return default
        try: return Decimal(str(val)) / Decimal('100')
        except: return default
    @staticmethod
    def _v(val, default=Decimal('0')) -> Decimal:
        if val is None: return default
        try: return Decimal(str(val))
        except: return default

    

    async def get_financial_indicators(self, symbol: str) -> "FinancialIndicators":
        """Fetch financial indicators from East Money and cninfo data."""
        from backend.schemas.stock import FinancialIndicators
        import re
        
        quote_data = {}
        try:
            params = {"secid": _secid(symbol), "fields": "f43,f44,f45,f46,f47,f48,f57,f58,f86,f100,f116,f117,f168,f169,f170"}
            resp = await self._http.get(EM_QUOTE_URL, params=params)
            quote_data = (resp.json()).get("data") or {}
        except Exception:
            pass
        
        name = str(quote_data.get("f58", symbol))
        pe = self._p(quote_data.get("f100"))
        pb_fin = self._p(quote_data.get("f86"))
        mcap = self._v(quote_data.get("f116"))
        tshares = self._v(quote_data.get("f117"))
        
        # Try to fetch financial data from East Money datacenter
        fin_data = {}
        try:
            dc_url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
            dc_params = {
                "reportName": "RPT_LICO_FN_CPD",
                "columns": "SECUCODE,BASIC_EPS,WEIGHTAVG_ROE,GROSSPROFIT_MARGIN,NETPROFIT_MARGIN,DEBT_ASSET_RATIO,CURRENT_RATIO,QUICK_RATIO,OPERATE_INCOME,NETPROFIT,PROFIT_DEDUCTED_NOT,CASHFLOW_OPERATE,OPERATE_INCOME_YOY,TOTAL_SHARES",
                "filter": f'(SECUCODE="{_secid(symbol)}")',
                "pageNumber": 1, "pageSize": 1,
                "sortTypes": -1, "sortColumns": "BASIC_EPS"
            }
            resp2 = await self._http.get(dc_url, params=dc_params)
            dc_result = (resp2.json()).get("result") or {}
            lists = dc_result.get("data") or []
            if lists:
                fin_data = lists[0]
        except Exception as e:
            logger.warning("East Money finance API failed: %s", e)
        
        def g(key: str, default=None):
            v = fin_data.get(key)
            return v if v is not None else default
        
        return FinancialIndicators(
            symbol=symbol, name=name,
            report_date=str(g("REPORT_DATE", "N/A")),
            net_profit=g("NETPROFIT"),
            deducted_net_profit=g("PROFIT_DEDUCTED_NOT"),
            gross_margin=g("GROSSPROFIT_MARGIN"),
            net_margin=g("NETPROFIT_MARGIN"),
            roe=g("WEIGHTAVG_ROE"),
            revenue=g("OPERATE_INCOME"),
            revenue_growth=g("OPERATE_INCOME_YOY"),
            debt_ratio=g("DEBT_ASSET_RATIO"),
            current_ratio=g("CURRENT_RATIO"),
            quick_ratio=g("QUICK_RATIO"),
            operating_cashflow=g("CASHFLOW_OPERATE"),
            total_shares=g("TOTAL_SHARES"),
            pe_ttm=float(pe) if pe else None,
            pb=float(pb_fin) if pb_fin else None,
            market_cap=float(mcap) if mcap else None,
        )


async def close(self) -> None:
        await self._http.aclose()