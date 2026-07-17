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
    format: str = Query(default="pdf", pattern="^(pdf|md)$"),
):
    from backend.services.analysis_service import analysis_service
    result = await analysis_service.analyze_stock(symbol, market=market, lookback_days=lookback_days)
    import os, io
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font("DejaVu", "", os.path.join(os.path.dirname(__file__), "..", "..", "..", "fonts", "DejaVuSans.ttf"), uni=True)
        pdf.add_font("DejaVu", "B", os.path.join(os.path.dirname(__file__), "..", "..", "..", "fonts", "DejaVuSans-Bold.ttf"), uni=True)
        lines = result.report_markdown.split("\n")
        for line in lines:
            if line.startswith("### "):
                pdf.set_font("DejaVu", "B", 12)
                pdf.cell(0, 8, line[4:], new_x="LMARGIN", new_y="NEXT")
            elif line.startswith("## "):
                pdf.set_font("DejaVu", "B", 14)
                pdf.cell(0, 9, line[3:], new_x="LMARGIN", new_y="NEXT")
            elif line.startswith("# "):
                pdf.set_font("DejaVu", "B", 16)
                pdf.cell(0, 10, line[2:], new_x="LMARGIN", new_y="NEXT")
            elif line.startswith("---"):
                pdf.cell(0, 5, "", new_x="LMARGIN", new_y="NEXT")
            elif line.strip().startswith("|"):
                pdf.set_font("DejaVu", "", 8)
                pdf.cell(0, 5, line.strip(), new_x="LMARGIN", new_y="NEXT")
            elif line.strip():
                pdf.set_font("DejaVu", "", 10)
                pdf.cell(0, 6, line[:120] if len(line) > 120 else line, new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(0, 4, "", new_x="LMARGIN", new_y="NEXT")
        buf = io.BytesIO()
        pdf.output(buf)
        filename = f"analysis_{symbol}_{market}_{lookback_days}d.pdf"
        return Response(
            content=buf.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
        )
    except ImportError:
        content = result.report_markdown
        filename = f"analysis_{symbol}_{market}_{lookback_days}d.md"
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
        )
