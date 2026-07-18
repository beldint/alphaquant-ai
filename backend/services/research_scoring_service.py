"""
Project: AlphaQuant AI
File: backend/services/research_scoring_service.py
Description: 100-point A-share research scoring model.
Python Version: 3.11.9
"""

# ruff: noqa: RUF001

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from backend.schemas.financial import FinancialIndicators


@dataclass(slots=True)
class ResearchScoreResult:
    """Weighted AI research scoring result."""

    symbol: str
    name: str
    fundamental_score: float
    solvency_score: float
    technical_score: float
    valuation_score: float
    risk_score: float
    total_score: float
    rating: str
    strengths: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    suggestion: str = ""
    raw_breakdown: dict[str, Any] = field(default_factory=dict)


class ResearchScoringService:
    """Score stocks using the configured 30/20/20/15/15 research framework."""

    def score(
        self,
        *,
        symbol: str,
        name: str,
        financials: FinancialIndicators | None,
        indicator_frame: pd.DataFrame,
        risk_summary: dict[str, Any],
    ) -> ResearchScoreResult:
        """
        Calculate the final research score.

        Args:
            symbol: Stock symbol.
            name: Stock name.
            financials: East Money financial indicators.
            indicator_frame: Python-calculated technical indicators.
            risk_summary: CNInfo risk summary.

        Returns:
            Weighted research score result.
        """
        fundamental_score = self._score_fundamentals(financials)
        solvency_score = self._score_solvency(financials)
        technical_score = self._score_technical(indicator_frame)
        valuation_score = self._score_valuation(financials)
        risk_score = self._score_risk(financials, risk_summary)
        total_score = round(
            fundamental_score
            + solvency_score
            + technical_score
            + valuation_score
            + risk_score,
            2,
        )
        strengths, risks = self._build_tags(
            fundamental_score=fundamental_score,
            solvency_score=solvency_score,
            technical_score=technical_score,
            valuation_score=valuation_score,
            risk_score=risk_score,
        )
        return ResearchScoreResult(
            symbol=symbol,
            name=name,
            fundamental_score=fundamental_score,
            solvency_score=solvency_score,
            technical_score=technical_score,
            valuation_score=valuation_score,
            risk_score=risk_score,
            total_score=total_score,
            rating=self._rating(total_score),
            strengths=strengths,
            risks=risks,
            suggestion=self._suggestion(total_score, technical_score, risk_score),
            raw_breakdown={
                "weights": {
                    "fundamental": 30,
                    "solvency": 20,
                    "technical": 20,
                    "valuation": 15,
                    "risk": 15,
                },
                "fundamental_indicators": {
                    "revenue": _value(financials, "revenue"),
                    "revenue_growth": _value(financials, "revenue_growth"),
                    "net_profit": _value(financials, "net_profit"),
                    "deducted_net_profit": _value(financials, "deducted_net_profit"),
                    "gross_margin": _value(financials, "gross_margin"),
                    "net_margin": _value(financials, "net_margin"),
                    "roe": _value(financials, "roe"),
                },
                "solvency_indicators": {
                    "debt_ratio": _value(financials, "debt_ratio"),
                    "current_ratio": _value(financials, "current_ratio"),
                    "quick_ratio": _value(financials, "quick_ratio"),
                    "cash": _value(financials, "cash"),
                    "interest_debt": _value(financials, "interest_debt"),
                    "operating_cashflow": _value(financials, "operating_cashflow"),
                },
                "technical_indicators": _technical_snapshot(indicator_frame),
                "valuation_indicators": {
                    "pe_ttm": _value(financials, "pe_ttm"),
                    "pb": _value(financials, "pb"),
                    "peg": _value(financials, "peg"),
                    "dividend_yield": _value(financials, "dividend_yield"),
                },
                "risk_indicators": {
                    "major_reduction": getattr(financials, "major_reduction", None)
                    if financials is not None
                    else None,
                    "pledge_ratio": _value(financials, "pledge_ratio"),
                    "goodwill": _value(financials, "goodwill"),
                    "auditor_change": getattr(financials, "auditor_change", None)
                    if financials is not None
                    else None,
                    "risk_count": int(risk_summary.get("risk_count") or 0),
                },
                "risk_summary": risk_summary,
            },
        )

    def _score_fundamentals(self, financials: FinancialIndicators | None) -> float:
        score = 0.0
        score += _range_score(
            _value(financials, "revenue_growth"),
            [(20, 6), (10, 5), (0, 3), (-10, 1)],
            2,
        )
        score += _positive_score(_value(financials, "net_profit"), 4)
        score += _positive_score(_value(financials, "deducted_net_profit"), 4)
        score += _range_score(
            _value(financials, "gross_margin"), [(40, 5), (25, 4), (15, 3), (5, 1)], 0
        )
        score += _range_score(
            _value(financials, "net_margin"), [(15, 4), (8, 3), (3, 2), (0, 1)], 0
        )
        score += _range_score(
            _value(financials, "roe"), [(20, 7), (15, 6), (10, 4), (5, 2)], 0
        )
        return min(round(score, 2), 30.0)

    def _score_solvency(self, financials: FinancialIndicators | None) -> float:
        score = 0.0
        debt_ratio = _value(financials, "debt_ratio")
        if debt_ratio is None:
            score += 3
        elif debt_ratio <= 40:
            score += 6
        elif debt_ratio <= 60:
            score += 4
        elif debt_ratio <= 75:
            score += 2
        score += _range_score(
            _value(financials, "current_ratio"), [(2, 4), (1.2, 3), (1, 2)], 0
        )
        score += _range_score(
            _value(financials, "quick_ratio"), [(1.5, 3), (1, 2), (0.8, 1)], 0
        )
        score += _positive_score(_value(financials, "cash"), 2)
        score += _inverse_positive_score(_value(financials, "interest_debt"), 2)
        score += _positive_score(_value(financials, "operating_cashflow"), 3)
        return min(round(score, 2), 20.0)

    def _score_technical(self, indicator_frame: pd.DataFrame) -> float:
        if indicator_frame.empty:
            return 8.0
        latest = indicator_frame.iloc[-1]
        close = _series_value(latest, "close")
        ma5 = _series_value(latest, "ma_5")
        ma10 = _series_value(latest, "ma_10")
        ma20 = _series_value(latest, "ma_20")
        ma60 = _series_value(latest, "ma_60")
        macd = _series_value(latest, "macd")
        macd_signal = _series_value(latest, "macd_signal") or _series_value(
            latest, "dea"
        )
        rsi = _series_value(latest, "rsi")
        kdj_k = _series_value(latest, "kdj_k") or _series_value(latest, "k")
        kdj_d = _series_value(latest, "kdj_d") or _series_value(latest, "d")
        boll_upper = _series_value(latest, "boll_upper")
        boll_lower = _series_value(latest, "boll_lower")
        score = 0.0
        if ma5 and ma10 and ma20 and ma60 and ma5 > ma10 > ma20 > ma60:
            score += 5
        elif ma5 and ma20 and ma60 and ma5 > ma20 > ma60:
            score += 4
        elif close and ma20 and close >= ma20:
            score += 3
        else:
            score += 1
        if macd is not None and macd_signal is not None and macd >= macd_signal:
            score += 4
        else:
            score += 1.5
        if rsi is None:
            score += 2
        elif 35 <= rsi <= 70:
            score += 4
        elif 25 <= rsi < 35 or 70 < rsi <= 80:
            score += 2.5
        else:
            score += 1
        if kdj_k is not None and kdj_d is not None and kdj_k >= kdj_d:
            score += 3
        else:
            score += 1
        if close and boll_upper and boll_lower and boll_lower <= close <= boll_upper:
            score += 4
        else:
            score += 1.5
        return min(round(score, 2), 20.0)

    def _score_valuation(self, financials: FinancialIndicators | None) -> float:
        score = 0.0
        pe = _value(financials, "pe_ttm")
        pb = _value(financials, "pb")
        peg = _value(financials, "peg")
        dividend_yield = _value(financials, "dividend_yield")
        score += _valuation_pe_score(pe)
        score += _valuation_pb_score(pb)
        score += _valuation_peg_score(peg)
        score += _range_score(dividend_yield, [(4, 3), (2, 2), (1, 1)], 0)
        return min(round(score, 2), 15.0)

    def _score_risk(
        self,
        financials: FinancialIndicators | None,
        risk_summary: dict[str, Any],
    ) -> float:
        score = 15.0
        risk_count = int(risk_summary.get("risk_count") or 0)
        score -= min(risk_count * 2.5, 8)
        if _value(financials, "goodwill") and _value(financials, "goodwill") > 0:
            score -= 1
        if (
            _value(financials, "pledge_ratio")
            and _value(financials, "pledge_ratio") > 30
        ):
            score -= 3
        if _value(financials, "debt_ratio") and _value(financials, "debt_ratio") > 75:
            score -= 2
        return max(round(score, 2), 0.0)

    def _build_tags(
        self,
        *,
        fundamental_score: float,
        solvency_score: float,
        technical_score: float,
        valuation_score: float,
        risk_score: float,
    ) -> tuple[list[str], list[str]]:
        strengths: list[str] = []
        risks: list[str] = []
        if fundamental_score >= 23:
            strengths.append("基本面质量较好")
        elif fundamental_score <= 12:
            risks.append("基本面评分偏低")
        if solvency_score >= 15:
            strengths.append("偿债能力较稳")
        elif solvency_score <= 8:
            risks.append("偿债指标偏弱")
        if technical_score >= 15:
            strengths.append("技术趋势较强")
        elif technical_score <= 8:
            risks.append("技术趋势偏弱")
        if valuation_score >= 10:
            strengths.append("估值相对合理")
        elif valuation_score <= 5:
            risks.append("估值性价比不足")
        if risk_score <= 8:
            risks.append("公告或财务风险需要重点跟踪")
        return strengths, risks

    def _rating(self, total_score: float) -> str:
        if total_score >= 85:
            return "A"
        if total_score >= 70:
            return "B"
        if total_score >= 55:
            return "C"
        return "D"

    def _suggestion(
        self,
        total_score: float,
        technical_score: float,
        risk_score: float,
    ) -> str:
        if risk_score <= 6:
            return "风险项较多，建议暂缓并等待公告风险消化。"
        if total_score >= 80 and technical_score >= 14:
            return "综合质量较好，可纳入重点观察并结合仓位纪律分批跟踪。"
        if total_score >= 65:
            return "具备一定研究价值，建议继续跟踪基本面和趋势确认。"
        if total_score >= 50:
            return "信号不够充分，建议观望。"
        return "综合评分偏低，建议回避或仅作长期观察。"


def _value(financials: FinancialIndicators | None, field_name: str) -> float | None:
    if financials is None:
        return None
    value = getattr(financials, field_name, None)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _series_value(row: pd.Series, field_name: str) -> float | None:
    value = row.get(field_name)
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _technical_snapshot(indicator_frame: pd.DataFrame) -> dict[str, float | None]:
    """Return the latest technical indicators required by the scoring framework."""
    if indicator_frame.empty:
        return {
            "ma5": None,
            "ma10": None,
            "ma20": None,
            "ma60": None,
            "macd": None,
            "rsi": None,
            "kdj_k": None,
            "kdj_d": None,
            "kdj_j": None,
            "boll_upper": None,
            "boll_mid": None,
            "boll_lower": None,
        }
    latest = indicator_frame.iloc[-1]
    return {
        "ma5": _series_value(latest, "ma_5"),
        "ma10": _series_value(latest, "ma_10"),
        "ma20": _series_value(latest, "ma_20"),
        "ma60": _series_value(latest, "ma_60"),
        "macd": _series_value(latest, "macd"),
        "rsi": _series_value(latest, "rsi"),
        "kdj_k": _series_value(latest, "kdj_k") or _series_value(latest, "k"),
        "kdj_d": _series_value(latest, "kdj_d") or _series_value(latest, "d"),
        "kdj_j": _series_value(latest, "kdj_j") or _series_value(latest, "j"),
        "boll_upper": _series_value(latest, "boll_upper"),
        "boll_mid": _series_value(latest, "boll_mid"),
        "boll_lower": _series_value(latest, "boll_lower"),
    }


def _positive_score(value: float | None, max_score: float) -> float:
    if value is None:
        return max_score * 0.4
    return max_score if value > 0 else 0


def _inverse_positive_score(value: float | None, max_score: float) -> float:
    if value is None:
        return max_score * 0.5
    return max_score if value <= 0 else max_score * 0.4


def _range_score(
    value: float | None,
    brackets: list[tuple[float, float]],
    default: float,
) -> float:
    if value is None:
        return default
    for threshold, score in brackets:
        if value >= threshold:
            return score
    return default


def _valuation_pe_score(pe: float | None) -> float:
    if pe is None or pe <= 0:
        return 2.0
    if pe <= 15:
        return 6.0
    if pe <= 30:
        return 4.5
    if pe <= 50:
        return 2.5
    return 1.0


def _valuation_pb_score(pb: float | None) -> float:
    if pb is None or pb <= 0:
        return 2.0
    if pb <= 2:
        return 6.0
    if pb <= 4:
        return 4.0
    if pb <= 8:
        return 2.0
    return 0.5


def _valuation_peg_score(peg: float | None) -> float:
    if peg is None or peg <= 0:
        return 1.0
    if peg <= 1:
        return 3.0
    if peg <= 2:
        return 2.0
    if peg <= 3:
        return 1.0
    return 0.0


research_scoring_service = ResearchScoringService()
