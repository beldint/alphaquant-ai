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
from backend.schemas.stock import QuoteResponse, StockResponse
from backend.services.stock_service import stock_service
from backend.services.scoring_service import StockScorer
from backend.schemas.analysis import StockScoreResponse


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


@router.get("/{symbol}/score", response_model=APIResponse[StockScoreResponse])
async def get_stock_score(
    symbol: str,
    market: str = Query(default="A", pattern="^(A|HK|US)$"),
) -> APIResponse[StockScoreResponse]:
    """Get 100-point stock score."""
    from datetime import date, timedelta
    from backend.datasource.providers.base import KlineBar, Market
    quote = await stock_service.get_realtime_quote(symbol, market)
    end = date.today()
    start = end - timedelta(days=120)
    bars = await stock_service.get_daily_kline(symbol, market=market, start_date=start, end_date=end)
    import pandas as pd
    frame = pd.DataFrame([
        {"trade_date": b.trade_date, "open": float(b.open_price), "high": float(b.high_price),
         "low": float(b.low_price), "close": float(b.close_price),
         "volume": float(b.volume), "amount": float(b.amount)} for b in bars
    ])
    if not frame.empty:
        frame = frame.sort_values("trade_date").set_index("trade_date")
        from backend.indicators.calculator import IndicatorCalculator
        calc = IndicatorCalculator()
        ind_frame = calc.calculate_all(frame)
        scorer = StockScorer()
        result = scorer.score_from_indicators(ind_frame, symbol=symbol, name=quote.name)
    else:
        from backend.services.scoring_service import StockScoreResult
        result = StockScoreResult(symbol=symbol, name=quote.name)
    return build_success_response(StockScoreResponse(
        symbol=result.symbol, name=result.name,
        total_score=result.total_score, tech_score=result.tech_score,
        volume_score=result.volume_score, fundamental_score=result.fundamental_score,
        valuation_score=result.valuation_score, sentiment_score=result.sentiment_score,
        summary=result.summary, strengths=result.strengths,
        risks=result.risks, suggestion=result.suggestion
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
    return build_success_response([bar.model_dump(mode="json") for bar in bars])
