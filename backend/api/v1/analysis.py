"""
Project: AlphaQuant AI
File: backend/api/v1/analysis.py
Description: AI stock analysis API routes.
Python Version: 3.11.9
"""

from __future__ import annotations

from fastapi import APIRouter, Query, Response

from backend.core.responses import APIResponse, build_success_response
from backend.schemas.analysis import StockAnalysisRequest, StockAnalysisResponse
from backend.services.analysis_service import analysis_service


router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/stock", response_model=APIResponse[StockAnalysisResponse])
async def analyze_stock(
    request: StockAnalysisRequest,
) -> APIResponse[StockAnalysisResponse]:
    """
    Generate AI analysis for a stock from real market data.

    Args:
        request: Stock analysis request.

    Returns:
        AI stock analysis response.
    """
    response = await analysis_service.analyze_stock(
        request.symbol,
        market=request.market,
        lookback_days=request.lookback_days,
    )
    return build_success_response(response)



@router.get("/download")
async def download_analysis(
    symbol: str = Query(min_length=1, max_length=32),
    market: str = Query(default="A"),
    lookback_days: int = Query(default=120, ge=20, le=1000),
):
    from backend.services.analysis_service import analysis_service
    try:
        import asyncio
        result = await asyncio.wait_for(
            analysis_service.analyze_stock(symbol, market=market, lookback_days=lookback_days),
            timeout=20
        )
        filename = f"analysis_{symbol}_{market}_{lookback_days}d.md"
        return Response(
            content=result.report_markdown,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        return Response(
            content="Analysis failed: " + str(e),
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="error.txt"'}
        )
