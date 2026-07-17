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
    format: str = Query(default="md", pattern="^(pdf|md)$"),
):
    from backend.services.analysis_service import analysis_service
    result = await analysis_service.analyze_stock(symbol, market=market, lookback_days=lookback_days)
    filename = f"analysis_{symbol}_{market}_{lookback_days}d"

    if format == "md":
        return Response(
            content=result.report_markdown,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{filename}.md"'}
        )

    import os, io, logging
    logger = logging.getLogger(__name__)
    try:
        from fpdf import FPDF
        _font_file = None
        _search_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "fonts", "NotoSansSC-Regular.ttf"),
            os.path.join("fonts", "NotoSansSC-Regular.ttf"),
        ]
        for _p in _search_paths:
            if os.path.exists(_p):
                _font_file = _p
                break
        if not _font_file:
            _cache_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "fonts")
            os.makedirs(_cache_dir, exist_ok=True)
            _font_file = os.path.join(_cache_dir, "NotoSansSC-Regular.ttf")
            if not os.path.exists(_font_file):
            except Exception:
        return Response(content=result.report_markdown, media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{filename}.md"'})
