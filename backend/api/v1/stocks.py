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
from backend.schemas.financial import FinancialIndicators
from backend.schemas.research import ResearchScoreResponse
from backend.schemas.stock import QuoteResponse, StockResponse
from backend.services.research_service import research_service
from backend.services.stock_service import stock_service

router = APIRouter(prefix="/stocks", tags=["stocks"])
KLINE_START_DATE_QUERY = Query(default=None)
KLINE_END_DATE_QUERY = Query(default=None)


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
            currency=(
                "CNY" if item.market == "A" else "HKD" if item.market == "HK" else "USD"
            ),
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


@router.get("/{symbol}/financials", response_model=APIResponse[FinancialIndicators])
async def get_financial_indicators(
    symbol: str,
    market: str = Query(default="A", pattern="^(A)$"),
) -> APIResponse[FinancialIndicators]:
    """
    Get East Money financial, valuation, and capital indicators.

    Args:
        symbol: Stock symbol.
        market: Market identifier. Currently A-share only.

    Returns:
        Financial indicator response.
    """
    _ = market
    indicators = await stock_service.get_financial_indicators(symbol)
    return build_success_response(indicators)


@router.get("/{symbol}/kline", response_model=APIResponse[list[dict[str, object]]])
async def get_kline(
    symbol: str,
    market: Literal["A", "HK", "US"] = Query(default="A"),
    start_date: date | None = KLINE_START_DATE_QUERY,
    end_date: date | None = KLINE_END_DATE_QUERY,
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


@router.get("/{symbol}/score", response_model=APIResponse[ResearchScoreResponse])
async def get_stock_score(
    symbol: str,
    market: str = Query(default="A", pattern="^(A|HK|US)$"),
) -> APIResponse[ResearchScoreResponse]:
    """
    Get 100-point stock score.

    Args:
        symbol: Stock symbol.
        market: Market identifier.

    Returns:
        Stock score response.
    """
    refresh = await research_service.refresh_stock(
        symbol,
        market=market,
        lookback_days=180,
        include_financials=True,
        include_risks=True,
    )
    return build_success_response(refresh.score)
