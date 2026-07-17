"""
Project: AlphaQuant AI
File: backend/services/analysis_service.py
Description: AI stock analysis orchestration service.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from backend.ai.providers.base import AICompletionRequest, AIMessage
from backend.ai.providers.factory import AIProviderFactory
from backend.cache.redis_client import redis_cache
from backend.core.config import settings
from backend.datasource.providers.base import Market
from backend.indicators.calculator import IndicatorCalculator
from backend.schemas.analysis import StockAnalysisResponse
from backend.services.stock_service import stock_service


class AnalysisService:
    """Application service for AI-driven stock analysis."""

    def __init__(self) -> None:
        """Initialize analysis service dependencies."""
        self.indicator_calculator = IndicatorCalculator()
        self.provider_factory = AIProviderFactory(settings)

    async def analyze_stock(
        self,
        symbol: str,
        *,
        market: Market = "A",
        lookback_days: int = 120,
        model: str | None = None,
        api_base_url: str | None = None,
        api_key: str | None = None,
    ) -> StockAnalysisResponse:
        if not model or not api_base_url or not api_key:
            from backend.core.exceptions import ConfigurationException
            raise ConfigurationException(
                "请在前端配置 AI 模型、API 地址和 API Key",
                setting_name="frontend_ai_config",
                details={"hint": "展开 AI 模型配置面板，填写模型名、API 地址和 API Key"},
            )
        """
        Generate an AI stock analysis report from real market data.

        Args:
            symbol: Stock symbol.
            market: Market identifier.
            lookback_days: Historical lookback window.

        Returns:
            AI stock analysis response.
        """
        cache_key = f"ai-analysis:{market}:{symbol}:{lookback_days}:{settings.ai_default_provider.value}"
        cached = await redis_cache.get_json(cache_key)
        if isinstance(cached, dict):
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
        objective_data = {
            "quote": quote.model_dump(mode="json"),
            "kline_count": len(bars),
            "start_date": str(start_date),
            "end_date": str(end_date),
        }
        technical_summary = self._build_technical_summary(indicator_frame)
        risk_summary = self._build_risk_summary(indicator_frame)
        report_markdown = await self._generate_report(
            symbol=symbol,
            market=market,
            objective_data=objective_data,
            technical_summary=technical_summary,
            risk_summary=risk_summary,
            model=model,
            api_base_url=api_base_url,
            api_key=api_key,
        )
        response = StockAnalysisResponse(
            symbol=symbol,
            market=market,
            provider=settings.ai_default_provider.value,
            model=settings.ai_analysis_model,
            report_markdown=report_markdown,
            objective_data=objective_data,
            technical_summary=technical_summary,
            risk_summary=risk_summary,
            data_timestamp=datetime.now().astimezone(),
        )
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
        risk_summary: dict[str, object],
        model: str | None = None,
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
            risk_summary: Risk summary.

        Returns:
            Markdown report.
        """
        provider = self.provider_factory.create_with_overrides(api_key=api_key, base_url=api_base_url, model=model)
        try:
            request = AICompletionRequest(
                model=settings.ai_analysis_model,
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens,
                messages=[
                    AIMessage(
                        role="system",
                        content=(
                            "你是专业股票分析助手。只能基于用户提供的真实数据分析，"
                            "不得编造行情、财务、新闻或确定性收益结论。"
                        ),
                    ),
                    AIMessage(
                        role="user",
                        content=(
                            f"股票代码：{symbol}\n市场：{market}\n"
                            f"客观数据：{objective_data}\n"
                            f"技术指标摘要：{technical_summary}\n"
                            f"风险摘要：{risk_summary}\n"
                            "请按以下结构输出 Markdown 报告：\n\n"
                            "## 📊 趋势分析\n"
                            "使用 ▁▂▃▄▅▆▇█ 绘制最近20个交易日价格趋势图（横轴时间，纵轴价格）。\n"
                            "分析MA5/MA10/MA20均线排列状态（多头/空头/缠绕），MACD柱线方向，RSI区间。\n"
                            "判断当前处于上升趋势、下降趋势还是震荡整理阶段。\n\n"
                            "## 📖 技术指标详解\n"
                            "对报告中每个技术指标给出中文全称和通俗解释：\n"
                            "- MACD：指数平滑异同移动平均线，判断趋势方向与力度\n"
                            "- RSI：相对强弱指标，衡量价格涨跌幅度，70以上超买、30以下超卖\n"
                            "- BOLL：布林带，由中轨(MA20)和上下轨组成，价格触及上下轨可能反转\n"
                            "- KDJ：随机指标，K/D/J三线交叉判断买卖时机\n"
                            "- MA：移动平均线，N日收盘价的算术平均\n\n"
                            "## 🧠 智能趋势识别\n"
                            "综合多时间维度给出趋势判断：\n"
                            "1. 短期趋势(1-5日)：基于K线形态、成交量变化、RSI\n"
                            "2. 中期趋势(1-4周)：基于MA排列、MACD方向、BOLL通道\n"
                            "3. 长期趋势(1-3月)：基于MA60/MA120、周线级别\n"
                            "4. 关键支撑/压力位：基于前高前低、均线位置、BOLL上下轨\n\n"
                            "## ⚠️ 风险提示\n"
                            "说明主要风险：趋势反转风险、成交量异常、指标背离等。"
                        ),
                    ),
                ],
            )
            completion = await provider.complete(request)
            return completion.content
        finally:
            await provider.close()

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
            "macd": latest.get("macd"),
            "rsi": latest.get("rsi"),
            "boll_upper": latest.get("boll_upper"),
            "boll_lower": latest.get("boll_lower"),
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
        volatility = float(returns.std() * (252 ** 0.5)) if not returns.empty else None
        max_close = frame["close"].cummax()
        drawdown = (frame["close"] / max_close - 1).min()
        return {
            "annualized_volatility": volatility,
            "max_drawdown": float(drawdown) if pd.notna(drawdown) else None,
            "data_points": int(len(frame)),
        }


analysis_service = AnalysisService()

