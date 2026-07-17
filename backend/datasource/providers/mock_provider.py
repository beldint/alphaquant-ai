from __future__ import annotations
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Literal
from random import uniform
from backend.core.config.settings import StockProviderName
from backend.datasource.providers.base import KlineBar, Market, RealtimeQuote, StockIdentity, StockProvider

MOCK_STOCKS = [
    StockIdentity(symbol='000001', name='平安银行', market='A', exchange='SZSE', industry='银行'),
    StockIdentity(symbol='000002', name='万科A', market='A', exchange='SZSE', industry='房地产'),
    StockIdentity(symbol='000333', name='美的集团', market='A', exchange='SZSE', industry='家用电器'),
    StockIdentity(symbol='000651', name='格力电器', market='A', exchange='SZSE', industry='家用电器'),
    StockIdentity(symbol='000725', name='京东方A', market='A', exchange='SZSE', industry='电子'),
    StockIdentity(symbol='000858', name='五粮液', market='A', exchange='SZSE', industry='食品饮料'),
    StockIdentity(symbol='002007', name='华兰生物', market='A', exchange='SZSE', industry='医药生物'),
    StockIdentity(symbol='002230', name='科大讯飞', market='A', exchange='SZSE', industry='计算机'),
    StockIdentity(symbol='002236', name='大华股份', market='A', exchange='SZSE', industry='计算机'),
    StockIdentity(symbol='002304', name='洋河股份', market='A', exchange='SZSE', industry='食品饮料'),
    StockIdentity(symbol='002352', name='顺丰控股', market='A', exchange='SZSE', industry='交通运输'),
    StockIdentity(symbol='002371', name='北方华创', market='A', exchange='SZSE', industry='电子'),
    StockIdentity(symbol='002415', name='海康威视', market='A', exchange='SZSE', industry='计算机'),
    StockIdentity(symbol='002459', name='晶澳科技', market='A', exchange='SZSE', industry='电力设备'),
    StockIdentity(symbol='002475', name='立讯精密', market='A', exchange='SZSE', industry='电子'),
    StockIdentity(symbol='002594', name='比亚迪', market='A', exchange='SZSE', industry='汽车'),
    StockIdentity(symbol='002714', name='牧原股份', market='A', exchange='SZSE', industry='农林牧渔'),
    StockIdentity(symbol='002812', name='恩捷股份', market='A', exchange='SZSE', industry='电力设备'),
    StockIdentity(symbol='300014', name='亿纬锂能', market='A', exchange='SZSE', industry='电力设备'),
    StockIdentity(symbol='300015', name='爱尔眼科', market='A', exchange='SZSE', industry='医药生物'),
    StockIdentity(symbol='300033', name='同花顺', market='A', exchange='SZSE', industry='计算机'),
    StockIdentity(symbol='300059', name='东方财富', market='A', exchange='SZSE', industry='非银金融'),
    StockIdentity(symbol='300122', name='智飞生物', market='A', exchange='SZSE', industry='医药生物'),
    StockIdentity(symbol='300124', name='汇川技术', market='A', exchange='SZSE', industry='电力设备'),
    StockIdentity(symbol='300274', name='阳光电源', market='A', exchange='SZSE', industry='电力设备'),
    StockIdentity(symbol='300308', name='中际旭创', market='A', exchange='SZSE', industry='通信'),
    StockIdentity(symbol='300413', name='芒果超媒', market='A', exchange='SZSE', industry='传媒'),
    StockIdentity(symbol='300433', name='蓝思科技', market='A', exchange='SZSE', industry='电子'),
    StockIdentity(symbol='300450', name='先导智能', market='A', exchange='SZSE', industry='电力设备'),
    StockIdentity(symbol='300498', name='温氏股份', market='A', exchange='SZSE', industry='农林牧渔'),
    StockIdentity(symbol='300502', name='新易盛', market='A', exchange='SZSE', industry='通信'),
    StockIdentity(symbol='300750', name='宁德时代', market='A', exchange='SZSE', industry='电力设备'),
    StockIdentity(symbol='300759', name='康龙化成', market='A', exchange='SZSE', industry='医药生物'),
    StockIdentity(symbol='300760', name='迈瑞医疗', market='A', exchange='SZSE', industry='医药生物'),
    StockIdentity(symbol='300782', name='卓胜微', market='A', exchange='SZSE', industry='电子'),
    StockIdentity(symbol='600036', name='招商银行', market='A', exchange='SSE', industry='银行'),
    StockIdentity(symbol='600276', name='恒瑞医药', market='A', exchange='SSE', industry='医药生物'),
    StockIdentity(symbol='600309', name='万华化学', market='A', exchange='SSE', industry='基础化工'),
    StockIdentity(symbol='600519', name='贵州茅台', market='A', exchange='SSE', industry='食品饮料'),
    StockIdentity(symbol='600585', name='海螺水泥', market='A', exchange='SSE', industry='建筑材料'),
    StockIdentity(symbol='600690', name='海尔智家', market='A', exchange='SSE', industry='家用电器'),
    StockIdentity(symbol='600809', name='山西汾酒', market='A', exchange='SSE', industry='食品饮料'),
    StockIdentity(symbol='600887', name='伊利股份', market='A', exchange='SSE', industry='食品饮料'),
    StockIdentity(symbol='600900', name='长江电力', market='A', exchange='SSE', industry='公用事业'),
    StockIdentity(symbol='600941', name='中国移动', market='A', exchange='SSE', industry='通信'),
    StockIdentity(symbol='601012', name='隆基绿能', market='A', exchange='SSE', industry='电力设备'),
    StockIdentity(symbol='601166', name='兴业银行', market='A', exchange='SSE', industry='银行'),
    StockIdentity(symbol='601318', name='中国平安', market='A', exchange='SSE', industry='非银金融'),
    StockIdentity(symbol='601328', name='交通银行', market='A', exchange='SSE', industry='银行'),
    StockIdentity(symbol='601398', name='工商银行', market='A', exchange='SSE', industry='银行'),
    StockIdentity(symbol='601628', name='中国人寿', market='A', exchange='SSE', industry='非银金融'),
    StockIdentity(symbol='601728', name='中国电信', market='A', exchange='SSE', industry='通信'),
    StockIdentity(symbol='601857', name='中国石油', market='A', exchange='SSE', industry='石油石化'),
    StockIdentity(symbol='601899', name='紫金矿业', market='A', exchange='SSE', industry='有色金属'),
    StockIdentity(symbol='601939', name='建设银行', market='A', exchange='SSE', industry='银行'),
    StockIdentity(symbol='688981', name='中芯国际', market='A', exchange='SSE', industry='电子'),
    StockIdentity(symbol='688041', name='海光信息', market='A', exchange='SSE', industry='电子'),
    StockIdentity(symbol='688256', name='寒武纪', market='A', exchange='SSE', industry='电子'),
    StockIdentity(symbol='688012', name='中微公司', market='A', exchange='SSE', industry='电子'),
    StockIdentity(symbol='000100', name='TCL科技', market='A', exchange='SZSE', industry='电子'),
    StockIdentity(symbol='000625', name='长安汽车', market='A', exchange='SZSE', industry='汽车'),
    StockIdentity(symbol='002129', name='TCL中环', market='A', exchange='SZSE', industry='电力设备'),
    StockIdentity(symbol='002466', name='天齐锂业', market='A', exchange='SZSE', industry='有色金属'),
    StockIdentity(symbol='002460', name='赣锋锂业', market='A', exchange='SZSE', industry='有色金属'),
    StockIdentity(symbol='002601', name='龙佰集团', market='A', exchange='SZSE', industry='基础化工'),
    StockIdentity(symbol='300676', name='华大基因', market='A', exchange='SZSE', industry='医药生物'),
    StockIdentity(symbol='300661', name='圣邦股份', market='A', exchange='SZSE', industry='电子'),
    StockIdentity(symbol='300124', name='汇川技术', market='A', exchange='SZSE', industry='电力设备'),
    StockIdentity(symbol='600028', name='中国石化', market='A', exchange='SSE', industry='石油石化'),
    StockIdentity(symbol='600104', name='上汽集团', market='A', exchange='SSE', industry='汽车'),
    StockIdentity(symbol='600745', name='闻泰科技', market='A', exchange='SSE', industry='电子'),
    StockIdentity(symbol='601088', name='中国神华', market='A', exchange='SSE', industry='煤炭'),
    StockIdentity(symbol='601766', name='中国中车', market='A', exchange='SSE', industry='机械设备'),
    StockIdentity(symbol='603259', name='药明康德', market='A', exchange='SSE', industry='医药生物'),
    StockIdentity(symbol='688396', name='华润微', market='A', exchange='SSE', industry='电子'),
    StockIdentity(symbol='688111', name='金山办公', market='A', exchange='SSE', industry='计算机'),
]

class MockStockProvider(StockProvider):
    provider_name = StockProviderName.TUSHARE
    def __init__(self):
        self._price = {}
    async def search_stocks(self, keyword, market='A'):
        result = [s for s in MOCK_STOCKS if keyword.lower() in s.symbol.lower() or keyword.lower() in s.name.lower()]
        return result if result else []
    async async def get_realtime_quote(self, symbol, market='A'):
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
    async async def get_daily_kline(self, symbol, market='A', start_date=None, end_date=None, adjust='qfq'):
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
