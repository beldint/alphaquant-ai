"""
Project: AlphaQuant AI
File: backend/tests/test_research_scoring.py
Description: Tests for A-share AI research scoring and database table contracts.
Python Version: 3.11.9
"""

from __future__ import annotations

import pandas as pd

from backend.models.research import CompanyRisk, FinancialReport, StockPrice, StockScore
from backend.schemas.financial import FinancialIndicators
from backend.services.research_scoring_service import research_scoring_service


def test_research_models_use_final_table_names() -> None:
    """Core research ORM models should match the final database design."""
    assert StockPrice.__tablename__ == "stock_price"
    assert FinancialReport.__tablename__ == "financial_report"
    assert CompanyRisk.__tablename__ == "company_risk"
    assert StockScore.__tablename__ == "stock_score"


def test_research_score_uses_100_point_weighting() -> None:
    """Research scoring should produce all five requested weighted dimensions."""
    financials = FinancialIndicators(
        symbol="600519",
        name="贵州茅台",
        revenue=1000000000,
        revenue_growth=15,
        net_profit=500000000,
        deducted_net_profit=480000000,
        gross_margin=60,
        net_margin=35,
        roe=25,
        debt_ratio=20,
        current_ratio=2.5,
        quick_ratio=2.0,
        cash=800000000,
        interest_debt=0,
        operating_cashflow=450000000,
        pe_ttm=25,
        pb=4,
        dividend_yield=2.5,
    )
    indicator_frame = pd.DataFrame(
        [
            {
                "close": 10,
                "ma_5": 11,
                "ma_20": 10,
                "ma_60": 9,
                "macd": 1,
                "macd_signal": 0.5,
                "rsi": 55,
                "kdj_k": 60,
                "kdj_d": 50,
                "boll_upper": 12,
                "boll_lower": 8,
            },
        ],
    )

    result = research_scoring_service.score(
        symbol="600519",
        name="贵州茅台",
        financials=financials,
        indicator_frame=indicator_frame,
        risk_summary={"source": "cninfo", "risk_count": 0},
    )

    assert result.fundamental_score <= 30
    assert result.solvency_score <= 20
    assert result.technical_score <= 20
    assert result.valuation_score <= 15
    assert result.risk_score <= 15
    assert result.total_score <= 100
    assert result.rating in {"A", "B", "C", "D"}
