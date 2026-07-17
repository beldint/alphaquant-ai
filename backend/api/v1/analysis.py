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

    import os, io, logging
    logger = logging.getLogger(__name__)
    filename = f"analysis_{symbol}_{market}_{lookback_days}d"

    if format == "md":
        return Response(
            content=result.report_markdown,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{filename}.md"''}'
        )

    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        font_paths = [
            os.path.join("fonts", "NotoSansSC-Regular.ttf"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "fonts", "NotoSansSC-Regular.ttf"),
        ]

        noto_path = None
        for fp in font_paths:
            if os.path.exists(fp):
                noto_path = fp
                break

        if not noto_path:
            cache_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "fonts")
            os.makedirs(cache_dir, exist_ok=True)
            noto_path = os.path.join(cache_dir, "NotoSansSC-Regular.ttf")
            if not os.path.exists(noto_path):
                try:
                    import httpx
                    url = "https://github.com/googlefonts/noto-cjk/releases/download/Sans2.004/03_NotoSansCJKsc.zip"
                    logger.warning("Noto font not available, falling back to markdown")
                    noto_path = None
                except Exception:
                    noto_path = None

        if noto_path and os.path.exists(noto_path):
            pdf.add_font("Noto", "", noto_path, uni=True)
            font_name = "Noto"
        else:
            return Response(
                content=result.report_markdown,
                media_type="text/markdown",
                headers={"Content-Disposition": f'attachment; filename="{filename}.md"''}'
            )

        lines = result.report_markdown.split("\n")
        for line in lines:
            if line.startswith("### "):
                pdf.set_font(font_name, "B", 12)
                pdf.cell(0, 8, line[4:], new_x="LMARGIN", new_y="NEXT")
            elif line.startswith("## "):
                pdf.set_font(font_name, "B", 14)
                pdf.cell(0, 9, line[3:], new_x="LMARGIN", new_y="NEXT")
            elif line.startswith("# "):
                pdf.set_font(font_name, "B", 16)
                pdf.cell(0, 10, line[2:], new_x="LMARGIN", new_y="NEXT")
            elif line.strip().startswith("|"):
                pdf.set_font(font_name, "", 8)
                pdf.cell(0, 5, line.strip()[:160] if len(line) > 160 else line.strip(), new_x="LMARGIN", new_y="NEXT")
            elif line.strip():
                pdf.set_font(font_name, "", 10)
                pdf.multi_cell(0, 6, line.strip())
            else:
                pdf.cell(0, 4, "", new_x="LMARGIN", new_y="NEXT")

        buf = io.BytesIO()
        pdf.output(buf)
        return Response(
            content=buf.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}.pdf"''}'
        )

    except ImportError:
        return Response(
            content=result.report_markdown,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{filename}.md"''}'
        )
