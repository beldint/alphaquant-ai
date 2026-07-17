"""
Project: AlphaQuant AI
File: backend/api/v1/stocks.py
Description: Stock market data API routes.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, Query

from backend.core.responses import APIResponse, build_success_response
from backend.schemas.stock import QuoteResponse, StockResponse, FinancialIndicators
from backend.services.stock_service import stock_service


router = APIRouter(prefix="/stocks", tags=["stocks"])
def _convert_kline(decimal_fields, bars):
    """Convert KlineBar Decimal fields to float for JSON serialization."""
    import json
    from decimal import Decimal
    result = []
    for bar in bars:
        d = bar.model_dump()
        for field in decimal_fields:
            val = d.get(field)
            if isinstance(val, Decimal):
                d[field] = float(val)
            elif isinstance(val, str):
                d[field] = float(val) if val.replace('.', '', 1).lstrip('-').isdigit() else val
        result.append(d)
    return result



@router.get("/search", response_model=APIResponse[list[StockResponse]])
async def search_stocks(
    keyword: str = Query(min_length=1, max_length=64),
    market: str = Query(default="A", pattern="^(A|HK|US)$"),
) -> APIResponse[list[StockResponse]]:
    """
    Search stocks by code or name.

    Args:
        keyword: Stock keyword.
        market: Market identifier.

    Returns:
        Matched stock list.
    """
    stocks = await stock_service.search_stocks(keyword, market)  # type: ignore[arg-type]
    response = [
        StockResponse(
            id=f"{item.market}:{item.symbol}",
            symbol=item.symbol,
            name=item.name,
            market=item.market,
            exchange=item.exchange,
            industry=item.industry,
            listing_date=None,
            currency="CNY" if item.market == "A" else "HKD" if item.market == "HK" else "USD",
            status="active",
        )
        for item in stocks
    ]
    return build_success_response(response)


@router.get("/{symbol}/quote", response_model=APIResponse[QuoteResponse])
async def get_quote(
    symbol: str,
    market: str = Query(default="A", pattern="^(A|HK|US)$"),
) -> APIResponse[QuoteResponse]:
    """
    Get realtime quote.

    Args:
        symbol: Stock symbol.
        market: Market identifier.

    Returns:
        Realtime quote response.
    """
    quote = await stock_service.get_realtime_quote(symbol, market)  # type: ignore[arg-type]
    return build_success_response(QuoteResponse.model_validate(quote.model_dump()))


@router.get("/{symbol}/kline", response_model=APIResponse[list[dict[str, object]]])
async def get_kline(


@router.get("/{symbol}/financials", response_model=APIResponse[FinancialIndicators])
async def get_financials(
    symbol: str,
    market: str = Query(default="A", pattern="^(A|HK|US)$"),
) -> APIResponse[FinancialIndicators]:
    """Get financial indicators for a stock."""
    quote = await stock_service.get_realtime_quote(symbol, market)
    name = quote.name
    # Try East Money finance API
    from backend.datasource.providers.eastmoney_provider import EastMoneyStockProvider
    em = EastMoneyStockProvider()
    try:
        fin = await em.get_financial_indicators(symbol)
        await em.close()
        return build_success_response(fin)
    except Exception:
        await em.close()
        # Fallback: return basic data from quote
        return build_success_response(FinancialIndicators(
            symbol=symbol, name=name,
            report_date="模拟数据",
            net_profit=0, deducted_net_profit=0, gross_margin=0, net_margin=0,
            roe=0, revenue=0, revenue_growth=0,
            debt_ratio=0, current_ratio=0, quick_ratio=0,
            cash=0, interest_debt=0, operating_cashflow=0,
            pe_ttm=0, pb=0, dividend_yield=0,
            inventory_days=0, ar_days=0, goodwill=0,
            pledge_ratio=0, market_cap=0, total_shares=0,
        ))

    symbol: str,
    market: Literal["A", "HK", "US"] = Query(default="A"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    adjust: Literal["none", "qfq", "hfq"] = Query(default="qfq"),
) -> APIResponse[list[dict[str, object]]]:
    """
    Get daily Kline data.

    Args:
        symbol: Stock symbol.
        market: Market identifier.
        start_date: Optional start date.
        end_date: Optional end date.
        adjust: Price adjustment mode.

    Returns:
        Kline data response.
    """
    bars = await stock_service.get_daily_kline(
        symbol,
        market=market,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )
    decimal_fields = ["open_price","high_price","low_price","close_price","volume","amount"]
    return build_success_response(_convert_kline(decimal_fields, bars))
