"""
Project: AlphaQuant AI
File: backend/services/research_service.py
Description: Data refresh, persistence, and scoring orchestration for A-share research.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

import pandas as pd
from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import transaction
from backend.datasource.providers.base import KlineBar, Market
from backend.indicators.calculator import IndicatorCalculator
from backend.models.research import CompanyRisk, FinancialReport, StockPrice, StockScore
from backend.schemas.financial import FinancialIndicators
from backend.schemas.research import ResearchRefreshResponse, ResearchScoreResponse
from backend.services.research_scoring_service import (
    ResearchScoreResult,
    research_scoring_service,
)
from backend.services.stock_service import stock_service


class ResearchService:
    """Refresh and persist research data for personal A-share analysis."""

    def __init__(self) -> None:
        """Initialize calculation dependencies."""
        self.indicator_calculator = IndicatorCalculator()

    async def refresh_stock(
        self,
        symbol: str,
        *,
        market: Market = "A",
        lookback_days: int = 180,
        include_financials: bool = True,
        include_risks: bool = True,
    ) -> ResearchRefreshResponse:
        """
        Refresh market, financial, risk, and score data for one stock.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            lookback_days: Kline lookback window.
            include_financials: Whether to refresh East Money financial data.
            include_risks: Whether to refresh CNInfo risk data.

        Returns:
            Refresh summary with the latest score.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days)
        quote = await stock_service.get_realtime_quote(symbol, market)
        bars = await stock_service.get_daily_kline(
            symbol,
            market=market,
            start_date=start_date,
            end_date=end_date,
        )
        financials = None
        if include_financials:
            try:
                financials = await stock_service.get_financial_indicators(symbol)
            except Exception as exc:
                logger.warning(
                    "Financial data unavailable for scoring: symbol={symbol} error={error}",
                    symbol=symbol,
                    error=str(exc),
                )
        risk_summary = await self._get_risk_summary(symbol, include_risks)
        indicator_frame = self._indicator_frame(bars)
        score = research_scoring_service.score(
            symbol=symbol,
            name=quote.name,
            financials=financials,
            indicator_frame=indicator_frame,
            risk_summary=risk_summary,
        )
        async with transaction() as session:
            await self._save_prices(session, bars)
            financial_saved = False
            if financials is not None:
                await self._save_financial_report(session, market, financials)
                financial_saved = True
            risk_rows = await self._save_risks(session, symbol, market, risk_summary)
            await self._save_score(session, market, score)
        logger.info(
            "Research refresh completed: symbol={symbol} prices={prices} risks={risks}",
            symbol=symbol,
            prices=len(bars),
            risks=risk_rows,
        )
        return ResearchRefreshResponse(
            symbol=symbol,
            market=market,
            refreshed_at=datetime.now().astimezone(),
            price_rows=len(bars),
            financial_saved=financial_saved,
            risk_rows=risk_rows,
            score=_to_score_response(score),
        )

    async def refresh_realtime_quotes(
        self,
        symbols: list[str],
        *,
        market: Market = "A",
    ) -> list[dict[str, object]]:
        """
        Refresh realtime quote cache for focused stocks during trading hours.

        Args:
            symbols: Focused stock symbols.
            market: Market identifier.

        Returns:
            Refreshed quote payloads.
        """
        results: list[dict[str, object]] = []
        for symbol in symbols:
            try:
                quote = await stock_service.get_realtime_quote(symbol, market)
                results.append(quote.model_dump(mode="json"))
            except Exception as exc:
                logger.warning(
                    "Realtime quote refresh failed: symbol={symbol} error={error}",
                    symbol=symbol,
                    error=str(exc),
                )
        return results

    async def refresh_after_close(
        self,
        symbols: list[str],
        *,
        market: Market = "A",
        lookback_days: int = 180,
    ) -> list[ResearchRefreshResponse]:
        """
        Run after-close Kline, indicator, and East Money financial refresh.

        Args:
            symbols: Stock symbols to refresh.
            market: Market identifier.
            lookback_days: Kline lookback window.

        Returns:
            Per-symbol refresh results.
        """
        results: list[ResearchRefreshResponse] = []
        for symbol in symbols:
            try:
                results.append(
                    await self.refresh_stock(
                        symbol,
                        market=market,
                        lookback_days=lookback_days,
                        include_financials=True,
                        include_risks=False,
                    ),
                )
            except Exception as exc:
                logger.warning(
                    "After-close refresh failed: symbol={symbol} error={error}",
                    symbol=symbol,
                    error=str(exc),
                )
        return results

    async def refresh_nightly_disclosures(
        self,
        symbols: list[str],
        *,
        market: Market = "A",
        lookback_days: int = 180,
    ) -> list[ResearchRefreshResponse]:
        """
        Run nightly CNInfo announcement, financial report, and risk refresh.

        Args:
            symbols: Stock symbols to refresh.
            market: Market identifier.
            lookback_days: Kline lookback window.

        Returns:
            Per-symbol refresh results.
        """
        results: list[ResearchRefreshResponse] = []
        for symbol in symbols:
            try:
                results.append(
                    await self.refresh_stock(
                        symbol,
                        market=market,
                        lookback_days=lookback_days,
                        include_financials=True,
                        include_risks=True,
                    ),
                )
            except Exception as exc:
                logger.warning(
                    "Nightly disclosure refresh failed: symbol={symbol} error={error}",
                    symbol=symbol,
                    error=str(exc),
                )
        return results

    async def get_latest_score(self, symbol: str) -> ResearchScoreResponse | None:
        """
        Get the latest persisted research score.

        Args:
            symbol: Stock symbol.

        Returns:
            Latest score or None.
        """
        async with transaction() as session:
            result = await session.execute(
                select(StockScore)
                .where(StockScore.symbol == symbol)
                .order_by(StockScore.score_date.desc(), StockScore.updated_at.desc())
                .limit(1),
            )
            score = result.scalar_one_or_none()
            if score is None:
                return None
            return ResearchScoreResponse(
                symbol=score.symbol,
                name=str(score.raw_breakdown.get("name") or score.symbol),
                score_date=score.score_date,
                fundamental_score=float(score.fundamental_score),
                solvency_score=float(score.solvency_score),
                technical_score=float(score.technical_score),
                valuation_score=float(score.valuation_score),
                risk_score=float(score.risk_score),
                total_score=float(score.total_score),
                rating=score.rating,
                strengths=list(score.strengths),
                risks=list(score.risks),
                suggestion=score.suggestion,
                raw_breakdown=dict(score.raw_breakdown),
            )

    def _indicator_frame(self, bars: list[KlineBar]) -> pd.DataFrame:
        records = [
            {
                "trade_date": item.trade_date,
                "open": float(item.open_price),
                "high": float(item.high_price),
                "low": float(item.low_price),
                "close": float(item.close_price),
                "volume": float(item.volume),
                "amount": float(item.amount),
            }
            for item in bars
        ]
        frame = pd.DataFrame.from_records(records)
        if frame.empty:
            return frame
        frame = frame.sort_values("trade_date").set_index("trade_date")
        return self.indicator_calculator.calculate_all(frame)

    async def _get_risk_summary(
        self,
        symbol: str,
        enabled: bool,
    ) -> dict[str, Any]:
        if not enabled:
            return {"source": "cninfo", "status": "disabled", "risk_count": 0}
        from backend.datasource.providers.cninfo_provider import CninfoProvider

        provider = CninfoProvider()
        try:
            return await provider.get_risk_signals(symbol)
        except Exception as exc:
            logger.warning(
                "CNInfo risk refresh failed: symbol={symbol} error={error}",
                symbol=symbol,
                error=str(exc),
            )
            return {
                "source": "cninfo",
                "status": "unavailable",
                "risk_count": 0,
                "error": str(exc),
            }
        finally:
            await provider.close()

    async def _save_prices(self, session: AsyncSession, bars: list[KlineBar]) -> None:
        for bar in bars:
            values = {
                "symbol": bar.symbol,
                "market": bar.market,
                "trade_date": bar.trade_date,
                "open_price": bar.open_price,
                "high_price": bar.high_price,
                "low_price": bar.low_price,
                "close_price": bar.close_price,
                "volume": bar.volume,
                "amount": bar.amount,
                "source": (
                    bar.source.value
                    if hasattr(bar.source, "value")
                    else str(bar.source)
                ),
            }
            await self._upsert(
                session,
                StockPrice,
                values,
                ["symbol", "trade_date"],
            )

    async def _save_financial_report(
        self,
        session: AsyncSession,
        market: Market,
        financials: FinancialIndicators,
    ) -> None:
        report_date = _parse_report_date(financials.report_date) or date.today()
        values = {
            "symbol": financials.symbol,
            "market": market,
            "report_date": report_date,
            "revenue": _decimal_or_none(financials.revenue),
            "revenue_growth": _decimal_or_none(financials.revenue_growth),
            "net_profit": _decimal_or_none(financials.net_profit),
            "deducted_net_profit": _decimal_or_none(financials.deducted_net_profit),
            "gross_margin": _decimal_or_none(financials.gross_margin),
            "net_margin": _decimal_or_none(financials.net_margin),
            "roe": _decimal_or_none(financials.roe),
            "debt_ratio": _decimal_or_none(financials.debt_ratio),
            "current_ratio": _decimal_or_none(financials.current_ratio),
            "quick_ratio": _decimal_or_none(financials.quick_ratio),
            "cash": _decimal_or_none(financials.cash),
            "interest_debt": _decimal_or_none(financials.interest_debt),
            "operating_cashflow": _decimal_or_none(financials.operating_cashflow),
            "pe_ttm": _decimal_or_none(financials.pe_ttm),
            "pb": _decimal_or_none(financials.pb),
            "peg": _decimal_or_none(financials.peg),
            "dividend_yield": _decimal_or_none(financials.dividend_yield),
            "market_cap": _decimal_or_none(financials.market_cap),
            "source": "eastmoney",
            "raw_data": financials.model_dump(mode="json"),
        }
        await self._upsert(
            session,
            FinancialReport,
            values,
            ["symbol", "report_date"],
        )

    async def _save_risks(
        self,
        session: AsyncSession,
        symbol: str,
        market: Market,
        risk_summary: dict[str, Any],
    ) -> int:
        risk_items = risk_summary.get("risk_announcements") or []
        if not isinstance(risk_items, list):
            return 0
        await session.execute(delete(CompanyRisk).where(CompanyRisk.symbol == symbol))
        saved = 0
        for item in risk_items:
            if not isinstance(item, dict):
                continue
            session.add(
                CompanyRisk(
                    symbol=symbol,
                    market=market,
                    risk_type=_classify_risk(str(item.get("title") or "")),
                    title=str(item.get("title") or "公告风险"),
                    severity="high",
                    source=str(item.get("source") or "cninfo"),
                    url=item.get("url"),
                    published_at=_parse_datetime(item.get("published_at")),
                    raw_data=item,
                ),
            )
            saved += 1
        return saved

    async def _save_score(
        self,
        session: AsyncSession,
        market: Market,
        score: ResearchScoreResult,
    ) -> None:
        values = {
            "symbol": score.symbol,
            "market": market,
            "score_date": date.today(),
            "fundamental_score": Decimal(str(score.fundamental_score)),
            "solvency_score": Decimal(str(score.solvency_score)),
            "technical_score": Decimal(str(score.technical_score)),
            "valuation_score": Decimal(str(score.valuation_score)),
            "risk_score": Decimal(str(score.risk_score)),
            "total_score": Decimal(str(score.total_score)),
            "rating": score.rating,
            "strengths": score.strengths,
            "risks": score.risks,
            "suggestion": score.suggestion,
            "raw_breakdown": {
                **score.raw_breakdown,
                "name": score.name,
            },
        }
        await self._upsert(session, StockScore, values, ["symbol", "score_date"])

    async def _upsert(
        self,
        session: AsyncSession,
        model: type,
        values: dict[str, Any],
        index_elements: list[str],
    ) -> None:
        if session.bind and session.bind.dialect.name == "postgresql":
            statement = pg_insert(model).values(**values)
            update_values = {
                key: getattr(statement.excluded, key)
                for key in values
                if key not in index_elements
            }
            await session.execute(
                statement.on_conflict_do_update(
                    index_elements=index_elements,
                    set_=update_values,
                ),
            )
            return
        filters = [
            getattr(model, field_name) == values[field_name]
            for field_name in index_elements
        ]
        existing = await session.execute(select(model).where(*filters).limit(1))
        instance = existing.scalar_one_or_none()
        if instance is None:
            session.add(model(**values))
            return
        for key, value in values.items():
            setattr(instance, key, value)


def _to_score_response(score: ResearchScoreResult) -> ResearchScoreResponse:
    return ResearchScoreResponse(
        symbol=score.symbol,
        name=score.name,
        score_date=date.today(),
        fundamental_score=score.fundamental_score,
        solvency_score=score.solvency_score,
        technical_score=score.technical_score,
        valuation_score=score.valuation_score,
        risk_score=score.risk_score,
        total_score=score.total_score,
        rating=score.rating,
        strengths=score.strengths,
        risks=score.risks,
        suggestion=score.suggestion,
        raw_breakdown=score.raw_breakdown,
    )


def _decimal_or_none(value: object) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _parse_report_date(value: str | None) -> date | None:
    if not value or value == "N/A":
        return None
    for pattern in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value[:19], pattern).date()
        except ValueError:
            continue
    return None


def _parse_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _classify_risk(title: str) -> str:
    mapping = {
        "减持": "major_reduction",
        "质押": "share_pledge",
        "审计": "audit_opinion",
        "退市": "delisting",
        "处罚": "regulatory_penalty",
        "监管": "regulatory_inquiry",
        "问询": "regulatory_inquiry",
        "诉讼": "litigation",
    }
    for keyword, risk_type in mapping.items():
        if keyword in title:
            return risk_type
    return "announcement_risk"


research_service = ResearchService()
