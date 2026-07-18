"""
Project: AlphaQuant AI
File: backend/services/analysis_service.py
Description: AI stock analysis orchestration service.
Python Version: 3.11.9
"""

# ruff: noqa: RUF001

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
from loguru import logger

from backend.ai.providers.base import AICompletionRequest, AIMessage
from backend.ai.providers.factory import AIProviderFactory
from backend.cache.redis_client import redis_cache
from backend.core.config import settings
from backend.core.config.settings import AIProviderName
from backend.datasource.providers.base import Market
from backend.datasource.providers.cninfo_provider import CninfoProvider
from backend.indicators.calculator import IndicatorCalculator
from backend.schemas.analysis import StockAnalysisResponse
from backend.services.stock_service import stock_service


class AnalysisService:
    """Application service for AI-driven stock analysis."""

    def __init__(self) -> None:
        """Initialize analysis service dependencies."""
        self.indicator_calculator = IndicatorCalculator()
        self.provider_factory = AIProviderFactory(settings)
        self.cninfo_provider = CninfoProvider()

    async def analyze_stock(
        self,
        symbol: str,
        *,
        market: Market = "A",
        lookback_days: int = 120,
        provider: AIProviderName | None = None,
        include_announcements: bool = True,
        include_financials: bool = True,
        model: str | None = None,
        api_base_url: str | None = None,
        api_key: str | None = None,
    ) -> StockAnalysisResponse:
        """
        Generate an AI stock analysis report from public market data.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            lookback_days: Historical lookback window.
            provider: Optional AI provider override.
            include_announcements: Whether to include CNInfo risk signals.
            include_financials: Whether to include East Money financial indicators.
            model: Optional AI model override.
            api_base_url: Optional OpenAI-compatible base URL override.
            api_key: Optional AI API key override.

        Returns:
            AI stock analysis response.
        """
        selected_provider = provider or settings.ai_default_provider
        selected_model = model or settings.ai_analysis_model
        cache_key = (
            f"ai-analysis:{market}:{symbol}:{lookback_days}:"
            f"{selected_provider.value}:{selected_model}:{include_financials}:{include_announcements}"
        )
        cached = await redis_cache.get_json(cache_key)
        if isinstance(cached, dict) and api_key is None and api_base_url is None:
            return StockAnalysisResponse.model_validate(cached)

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=lookback_days)
        quote = await stock_service.get_realtime_quote(symbol, market)
        bars = await stock_service.get_daily_kline(
            symbol,
            market=market,
            start_date=start_date,
            end_date=end_date,
        )
        frame = self._bars_to_frame(bars)
        indicator_frame = self.indicator_calculator.calculate_all(frame)
        financial_summary = await self._build_financial_summary(
            symbol, include_financials
        )
        official_risk_summary = await self._build_official_risk_summary(
            symbol, include_announcements
        )
        objective_data = {
            "quote": quote.model_dump(mode="json"),
            "kline_count": len(bars),
            "start_date": str(start_date),
            "end_date": str(end_date),
            "market_data_sources": {
                "quote": (
                    quote.source.value
                    if hasattr(quote.source, "value")
                    else str(quote.source)
                ),
                "kline": bars[-1].source.value if bars else None,
                "financials": financial_summary.get("source"),
                "official_disclosure": official_risk_summary.get("source"),
            },
        }
        technical_summary = self._build_technical_summary(indicator_frame)
        risk_summary = {
            **self._build_risk_summary(indicator_frame),
            "official_disclosure": official_risk_summary,
        }
        report_markdown = await self._generate_report(
            symbol=symbol,
            market=market,
            objective_data=objective_data,
            technical_summary=technical_summary,
            financial_summary=financial_summary,
            risk_summary=risk_summary,
            provider=selected_provider,
            model=selected_model,
            api_base_url=api_base_url,
            api_key=api_key,
        )
        response = StockAnalysisResponse(
            symbol=symbol,
            market=market,
            provider=selected_provider.value,
            model=selected_model,
            report_markdown=report_markdown,
            objective_data=objective_data,
            technical_summary=technical_summary,
            risk_summary=risk_summary,
            data_timestamp=datetime.now().astimezone(),
        )
        if api_key is None and api_base_url is None:
            await redis_cache.set_json(
                cache_key,
                response.model_dump(mode="json"),
                ttl_seconds=settings.ai_analysis_cache_ttl_seconds,
            )
        return response

    async def _generate_report(
        self,
        *,
        symbol: str,
        market: Market,
        objective_data: dict[str, object],
        technical_summary: dict[str, object],
        financial_summary: dict[str, object],
        risk_summary: dict[str, object],
        provider: AIProviderName,
        model: str,
        api_base_url: str | None = None,
        api_key: str | None = None,
    ) -> str:
        """
        Generate Markdown analysis report through the configured AI provider.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            objective_data: Objective market data.
            technical_summary: Calculated technical signals.
            financial_summary: East Money financial and valuation signals.
            risk_summary: Quantitative and official disclosure risks.
            provider: AI provider.
            model: AI model.
            api_base_url: Optional API base URL override.
            api_key: Optional API key override.

        Returns:
            Markdown report.
        """
        ai_provider = self.provider_factory.create_with_overrides(
            provider_name=provider,
            api_key=api_key,
            base_url=api_base_url,
            model=model,
        )
        try:
            request = AICompletionRequest(
                model=model,
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens,
                messages=[
                    AIMessage(
                        role="system",
                        content=(
                            "你是专业股票分析助手。只能基于用户提供的公开市场数据、"
                            "技术指标、东方财富财务估值数据和巨潮资讯公告风险信息进行分析。"
                            "不得编造行情、财务、公告、新闻或确定性收益结论。"
                        ),
                    ),
                    AIMessage(
                        role="user",
                        content=self._build_prompt(
                            symbol=symbol,
                            market=market,
                            objective_data=objective_data,
                            technical_summary=technical_summary,
                            financial_summary=financial_summary,
                            risk_summary=risk_summary,
                        ),
                    ),
                ],
            )
            completion = await ai_provider.complete(request)
            return completion.content
        finally:
            await ai_provider.close()

    def _build_prompt(
        self,
        *,
        symbol: str,
        market: Market,
        objective_data: dict[str, object],
        technical_summary: dict[str, object],
        financial_summary: dict[str, object],
        risk_summary: dict[str, object],
    ) -> str:
        """
        Build the Chinese prompt sent to the AI provider.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            objective_data: Objective data payload.
            technical_summary: Technical indicator summary.
            financial_summary: Financial summary.
            risk_summary: Risk summary.

        Returns:
            Prompt text.
        """
        return (
            f"股票代码：{symbol}\n"
            f"市场：{market}\n"
            f"客观行情数据：{objective_data}\n"
            f"Python 技术指标摘要：{technical_summary}\n"
            f"东方财富财务与估值摘要：{financial_summary}\n"
            f"量化风险与巨潮资讯官方风险摘要：{risk_summary}\n\n"
            "请输出 Markdown 股票投资分析报告，结构如下：\n\n"
            "## 1. 数据来源与时间\n"
            "说明行情、K线、财务估值和公告风险数据的来源与时间范围。\n\n"
            "## 2. 趋势分析\n"
            "基于最近交易日收盘价、MA5、MA20、MACD、RSI、BOLL 等指标"
            "判断短中期趋势。\n\n"
            "## 3. 技术指标详解\n"
            "用通俗中文解释 MACD、RSI、KDJ、BOLL、MA、ATR 等指标"
            "当前含义，并说明是否形成共振或背离。\n\n"
            "## 4. 资金与估值观察\n"
            "结合东方财富提供的 PE、PB、市值、ROE、收入增长、现金流等数据，"
            "分析估值和基本面质量。\n\n"
            "## 5. 官方公告与风险提示\n"
            "结合巨潮资讯公告风险关键词，说明可能的监管、诉讼、减持、质押、退市或财报更正风险。\n\n"
            "## 6. 综合判断\n"
            "给出机会、风险、观察位和适合继续跟踪的条件。不要承诺未来收益。"
        )

    def _bars_to_frame(self, bars: list[object]) -> pd.DataFrame:
        """
        Convert Kline bars into an OHLCV dataframe.

        Args:
            bars: Kline bar objects.

        Returns:
            OHLCV dataframe indexed by trade date.
        """
        records = [
            {
                "trade_date": bar.trade_date,
                "open": float(bar.open_price),
                "high": float(bar.high_price),
                "low": float(bar.low_price),
                "close": float(bar.close_price),
                "volume": float(bar.volume),
                "amount": float(bar.amount),
            }
            for bar in bars
        ]
        frame = pd.DataFrame.from_records(records)
        if frame.empty:
            return pd.DataFrame(
                columns=["open", "high", "low", "close", "volume", "amount"],
            )
        frame = frame.sort_values("trade_date").set_index("trade_date")
        return frame

    async def _build_financial_summary(
        self,
        symbol: str,
        enabled: bool,
    ) -> dict[str, object]:
        if not enabled:
            return {"source": "eastmoney", "status": "disabled"}
        try:
            indicators = await stock_service.get_financial_indicators(symbol)
            return indicators.model_dump(mode="json")
        except Exception as exc:
            logger.warning(
                "Financial summary unavailable: symbol={symbol} error={error}",
                symbol=symbol,
                error=str(exc),
            )
            return {"source": "eastmoney", "status": "unavailable", "error": str(exc)}

    async def _build_official_risk_summary(
        self,
        symbol: str,
        enabled: bool,
    ) -> dict[str, object]:
        if not enabled:
            return {"source": "cninfo", "status": "disabled"}
        try:
            return await self.cninfo_provider.get_risk_signals(symbol)
        except Exception as exc:
            logger.warning(
                "CNInfo risk summary unavailable: symbol={symbol} error={error}",
                symbol=symbol,
                error=str(exc),
            )
            return {"source": "cninfo", "status": "unavailable", "error": str(exc)}

    def _build_technical_summary(self, frame: pd.DataFrame) -> dict[str, object]:
        """
        Build compact technical summary from indicator dataframe.

        Args:
            frame: Indicator dataframe.

        Returns:
            Technical summary dictionary.
        """
        if frame.empty:
            return {"status": "insufficient_data"}
        latest = frame.iloc[-1].dropna().to_dict()
        return {
            "latest_close": latest.get("close"),
            "ma_5": latest.get("ma_5"),
            "ma_20": latest.get("ma_20"),
            "ema_12": latest.get("ema_12"),
            "macd": latest.get("macd"),
            "macd_signal": latest.get("macd_signal"),
            "rsi": latest.get("rsi"),
            "kdj_k": latest.get("kdj_k"),
            "kdj_d": latest.get("kdj_d"),
            "boll_upper": latest.get("boll_upper"),
            "boll_middle": latest.get("boll_middle"),
            "boll_lower": latest.get("boll_lower"),
            "atr": latest.get("atr"),
            "obv": latest.get("obv"),
        }

    def _build_risk_summary(self, frame: pd.DataFrame) -> dict[str, object]:
        """
        Build compact risk summary from indicator dataframe.

        Args:
            frame: Indicator dataframe.

        Returns:
            Risk summary dictionary.
        """
        if frame.empty or "close" not in frame:
            return {"status": "insufficient_data"}
        returns = frame["close"].pct_change().dropna()
        volatility = float(returns.std() * (252**0.5)) if not returns.empty else None
        max_close = frame["close"].cummax()
        drawdown = (frame["close"] / max_close - 1).min()
        latest_close = float(frame["close"].iloc[-1])
        recent_high = (
            float(frame["high"].tail(60).max()) if "high" in frame else latest_close
        )
        recent_low = (
            float(frame["low"].tail(60).min()) if "low" in frame else latest_close
        )
        return {
            "annualized_volatility": volatility,
            "max_drawdown": float(drawdown) if pd.notna(drawdown) else None,
            "data_points": len(frame),
            "recent_60d_high": recent_high,
            "recent_60d_low": recent_low,
            "distance_to_60d_high_pct": _pct_distance(latest_close, recent_high),
            "distance_to_60d_low_pct": _pct_distance(latest_close, recent_low),
        }


def _pct_distance(current: float, anchor: float) -> float | None:
    if anchor == 0:
        return None
    return round((current / anchor - 1) * 100, 2)


analysis_service = AnalysisService()
