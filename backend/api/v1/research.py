"""
Project: AlphaQuant AI
File: backend/api/v1/research.py
Description: Personal A-share AI research workflow API routes.
Python Version: 3.11.9
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.core.exceptions import NotFoundException
from backend.core.responses import APIResponse, build_success_response
from backend.schemas.research import (
    ResearchRefreshRequest,
    ResearchRefreshResponse,
    ResearchScoreResponse,
)
from backend.services.research_service import research_service

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/refresh", response_model=APIResponse[ResearchRefreshResponse])
async def refresh_research_data(
    request: ResearchRefreshRequest,
) -> APIResponse[ResearchRefreshResponse]:
    """
    Refresh market, financial, risk, and score data for one A-share stock.

    Args:
        request: Refresh request.

    Returns:
        Refresh summary.
    """
    result = await research_service.refresh_stock(
        request.symbol,
        market=request.market,
        lookback_days=request.lookback_days,
        include_financials=request.include_financials,
        include_risks=request.include_risks,
    )
    return build_success_response(result)


@router.get("/{symbol}/score", response_model=APIResponse[ResearchScoreResponse])
async def get_latest_research_score(
    symbol: str,
) -> APIResponse[ResearchScoreResponse]:
    """
    Get the latest persisted 100-point research score.

    Args:
        symbol: Stock symbol.

    Returns:
        Latest research score.
    """
    score = await research_service.get_latest_score(symbol)
    if score is None:
        raise NotFoundException(
            "Research score not found",
            resource="stock_score",
            identifier=symbol,
        )
    return build_success_response(score)
