from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from backend.schemas.common import ORMModel

class FinancialIndicators(BaseModel):
    """Financial indicator response schema."""
    model_config = ConfigDict()
    symbol: str
    name: str
    # Profitability
    net_profit: float | None = None
    deducted_net_profit: float | None = None
    gross_margin: float | None = None
    net_margin: float | None = None
    roe: float | None = None
    revenue: float | None = None
    revenue_growth: float | None = None
    # Debt safety
    debt_ratio: float | None = None
    current_ratio: float | None = None
    quick_ratio: float | None = None
    cash: float | None = None
    interest_debt: float | None = None
    operating_cashflow: float | None = None
    # Valuation
    pe_ttm: float | None = None
    pb: float | None = None
    dividend_yield: float | None = None
    # Operations
    inventory_days: float | None = None
    ar_days: float | None = None
    goodwill: float | None = None
    # Risk
    pledge_ratio: float | None = None
    major_reduction: str | None = None
    auditor_change: str | None = None
    # Market cap
    market_cap: float | None = None
    total_shares: float | None = None
    report_date: str | None = None

