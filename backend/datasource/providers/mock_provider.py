from __future__ import annotations
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Literal
from random import uniform
from backend.core.config.settings import StockProviderName
from backend.datasource.providers.base import KlineBar, Market, RealtimeQuote, StockIdentity, StockProvider

MOCK_STOCKS = [
    StockIdentity(symbol='000001', name='平安银行', market='A', exchange='SZSE', industry='银行'),
    StockIdentity(symbol='000333', name='美的集团', market='A', exchange='SZSE', industry='家用电器'),
    StockIdentity(symbol='600519', name='贵州茅台', market='A', exchange='SSE', industry='食品饮料'),
    StockIdentity(symbol='000858', name='五粮液', market='A', exchange='SZSE', industry='食品饮料'),
    StockIdentity(symbol='300750', name='宁德时代', market='A', exchange='SZSE', industry='电力设备'),
    StockIdentity(symbol='601318', name='中国平安', market='A', exchange='SSE', industry='保险'),
    StockIdentity(symbol='600036', name='招商银行', market='A', exchange='SSE', industry='银行'),
    StockIdentity(symbol='000002', name='万科A', market='A', exchange='SZSE', industry='房地产'),
    StockIdentity(symbol='600900', name='长江电力', market='A', exchange='SSE', industry='公用事业'),
    StockIdentity(symbol='688981', name='中芯国际', market='A', exchange='SSE', industry='电子'),
]

class MockStockProvider(StockProvider):
    provider_name = StockProviderName.TUSHARE
    def __init__(self):
        self._price = {}
    async def search_stocks(self, keyword, market='A'):
        result = [s for s in MOCK_STOCKS if keyword.lower() in s.symbol.lower() or keyword.lower() in s.name.lower()]
        return result if result else MOCK_STOCKS[:5]
    async def get_realtime_quote(self, symbol, market='A'):
        name = next((s.name for s in MOCK_STOCKS if s.symbol == symbol), symbol)
        if symbol not in self._price:
            self._price[symbol] = round(uniform(10, 500), 2)
        p = self._price[symbol]
        chg = round(uniform(-5, 5), 2)
        pct = round(chg / p * 100, 2) if p else 0
        return RealtimeQuote(symbol=symbol, name=name, market=market,
            price=Decimal(str(p)), change=Decimal(str(chg)),
            pct_change=Decimal(str(pct)),
            volume=Decimal(str(int(uniform(1e6, 1e8)))),
            amount=Decimal(str(int(uniform(1e7, 1e9)))),
            timestamp=datetime.now().astimezone(), source=StockProviderName.TUSHARE)
    async def get_daily_kline(self, symbol, market='A', start_date=None, end_date=None, adjust='qfq'):
        end = end_date or datetime.now().date()
        start = start_date or (end - timedelta(days=120))
        bars, price = [], Decimal(str(round(uniform(10, 500), 2)))
        d = start
        while d <= end:
            if d.weekday() < 5:
                cp = (price * Decimal(str(round(uniform(0.95, 1.05), 4)))).quantize(Decimal('0.01'))
                hp = max(price, cp) * Decimal(str(round(uniform(1, 1.03), 4)))
                lp = min(price, cp) * Decimal(str(round(uniform(0.97, 1), 4)))
                bars.append(KlineBar(symbol=symbol, market=market, trade_date=d,
                    open_price=price.quantize(Decimal('0.01')),
                    high_price=hp.quantize(Decimal('0.01')),
                    low_price=lp.quantize(Decimal('0.01')),
                    close_price=cp,
                    volume=Decimal(str(int(uniform(1e6, 5e7)))),
                    amount=Decimal(str(int(uniform(1e7, 1e9)))),
                    source=StockProviderName.TUSHARE))
                price = cp
            d += timedelta(days=1)
        return bars
