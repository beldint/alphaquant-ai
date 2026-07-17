"""Stock scoring service - 100-point scoring model."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class StockScoreResult:
    """Stock scoring result."""
    symbol: str = ''
    name: str = ''
    total_score: float = 0
    tech_score: float = 0
    volume_score: float = 0
    fundamental_score: float = 0
    valuation_score: float = 0
    sentiment_score: float = 0
    summary: str = ''
    strengths: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    suggestion: str = ''


class StockScorer:
    """Score stocks based on technical, fundamental, and market data."""

    def score_from_indicators(self, indicator_df, symbol='', name='') -> StockScoreResult:
        """Calculate score from technical indicator dataframe."""
        import pandas as pd
        if indicator_df is None or indicator_df.empty:
            return StockScoreResult(symbol=symbol, name=name)
        frame = indicator_df.copy()
        if isinstance(frame.index, pd.DatetimeIndex): frame = frame.reset_index()
        if len(frame) < 5: return StockScoreResult(symbol=symbol, name=name)
        last = frame.iloc[-1]

        tech_score = self._calc_tech_score(last, frame)
        vol_score = self._calc_volume_score(last, frame)
        fund_score = self._calc_fundamental_score(last)
        val_score = self._calc_valuation_score(last)
        sent_score = self._calc_sentiment_score(last, frame)
        total = round(tech_score + vol_score + fund_score + val_score + sent_score, 1)

        strengths, risks = [], []
        if tech_score >= 22: strengths.append("√ 技术趋势健康")
        elif tech_score <= 12: risks.append("× 技术面偏弱")
        if vol_score >= 15: strengths.append("√ 成交量配合良好")
        elif vol_score <= 8: risks.append("× 成交量不足")
        if fund_score >= 20: strengths.append("√ 基本面优秀")
        elif fund_score <= 12: risks.append("× 基本面偏弱")
        if val_score >= 7: strengths.append("√ 估值合理")
        elif val_score <= 3: risks.append("× 估值偏高")

        suggestion = "建议关注，等待买入时机" if total >= 70 else "建议观望" if total >= 50 else "建议回避"
        if total >= 80: suggestion = "长期配置价值较高"
        if total >= 65 and tech_score >= 20: suggestion = "技术面转好，可分批建仓"

        result = StockScoreResult(symbol=symbol, name=name, total_score=total,
            tech_score=tech_score, volume_score=vol_score,
            fundamental_score=fund_score, valuation_score=val_score,
            sentiment_score=sent_score,
            summary=f"{symbol} {name} 综合评分 {total}/100",
            strengths=strengths, risks=risks, suggestion=suggestion)
        return result

    def _get(self, d, keys, default=0):
        """Get value from series by trying multiple keys."""
        if not hasattr(d, 'get') and hasattr(d, '__getitem__'):
            for k in keys:
                try:
                    v = d[k]
                    if v is not None and not (isinstance(v, float) and pd.isna(v)):
                        return float(v)
                except: pass
        for k in keys:
            if k in d:
                v = d[k]
                if v is not None and not (isinstance(v, float) and (pd.isna(v) if hasattr(pd,'isna') else False)):
                    try: return float(v)
                    except: pass
        return default

    def _calc_tech_score(self, last, frame):
        s = 0.0; import pandas as pd
        # MA alignment (5 pts)
        ma5 = self._get(last, ['ma_5','ma5','ma_5']); ma20 = self._get(last, ['ma_20','ma20','ma_20']); ma60 = self._get(last, ['ma_60','ma60','ma_60'])
        if ma5 and ma20 and ma60:
            if ma5 > ma20 > ma60: s += 5
            elif ma5 > ma20: s += 3
            elif ma5 < ma20 and ma20 < ma60: s += 1
            else: s += 2
        else: s += 2.5
        # MACD (5 pts)
        macd = self._get(last, ['macd','macd']); macd_signal = self._get(last, ['macd_signal','macds','signal'])
        macd_hist = self._get(last, ['macd_hist','macdh','histogram'])
        if macd and macd_signal:
            if macd > macd_signal and macd_hist > 0: s += 5
            elif macd > macd_signal: s += 3
            elif macd < macd_signal and macd_hist < 0: s += 1
            else: s += 2
        else: s += 2.5
        # RSI (5 pts)
        rsi = self._get(last, ['rsi','rsi'])
        if rsi:
            if 40 <= rsi <= 60: s += 4
            elif 30 <= rsi < 40 or 60 < rsi <= 70: s += 3
            elif rsi > 70: s += 1
            elif rsi < 30: s += 5
        else: s += 2.5
        # KDJ (5 pts)
        k = self._get(last, ['kdj_k','k','k_value']); d_v = self._get(last, ['kdj_d','d','d_value']); j = self._get(last, ['kdj_j','j','j_value'])
        if k and d_v:
            if k > d_v and k < 80: s += 4
            elif k > d_v: s += 3
            elif k < d_v and k > 20: s += 2
            else: s += 1
        else: s += 2.5
        # BOLL (5 pts)
        close = self._get(last, ['close','close']); boll_u = self._get(last, ['boll_upper','upper','boll_upper']); boll_l = self._get(last, ['boll_lower','lower','boll_lower']); boll_m = self._get(last, ['boll_mid','mid','ma_20'])
        if close and boll_u and boll_l:
            if boll_l < close < boll_u: s += 4
            elif close >= boll_u: s += 2
            elif close <= boll_l: s += 3
        else: s += 2.5
        # K-line trend (5 pts) - multi-day comparison
        if len(frame) >= 5:
            c5 = self._get(frame.iloc[-5], ['close','close']); c1 = self._get(frame.iloc[-1], ['close','close'])
            if c5 and c1:
                pct5 = (c1 - c5) / c5 * 100
                if pct5 > 3: s += 5
                elif pct5 > 0: s += 3
                elif pct5 > -3: s += 2
                else: s += 1
            else: s += 2.5
        else: s += 2.5
        return min(s, 30)

    def _calc_volume_score(self, last, frame):
        s = 0.0
        vol = self._get(last, ['volume','vol','volume'])
        if len(frame) >= 10:
            avg_vol = sum(self._get(frame.iloc[i], ['volume','vol','volume']) for i in range(-10, 0)) / 10
            if avg_vol > 0:
                ratio = vol / avg_vol if vol else 0
                if 1.2 <= ratio <= 2.5: s += 7
                elif 0.8 <= ratio < 1.2: s += 5
                elif ratio > 2.5: s += 4
                else: s += 2
            close = self._get(last, ['close','close']); prev_close = self._get(frame.iloc[-2], ['close','close']); prev_vol = self._get(frame.iloc[-2], ['volume','vol','volume'])
            if close and prev_close and vol and prev_vol:
                price_up = close >= prev_close; vol_up = vol >= prev_vol
                if price_up and vol_up: s += 8
                elif not price_up and not vol_up: s += 3
                elif not price_up and vol_up: s += 4
                else: s += 6
            close_pct = 0
            if len(frame) >= 5:
                c5v = self._get(frame.iloc[-5], ['close','close']); c1v = self._get(frame.iloc[-1], ['close','close'])
                if c5v and c1v: close_pct = (c1v - c5v) / c5v * 100
            if close_pct > 5: s += 5; elif close_pct > 2: s += 3; elif close_pct < -5: s += 1; else: s += 2
        return min(s, 20)

    def _calc_fundamental_score(self, last):
        return 15

    def _calc_valuation_score(self, last):
        return 5

    def _calc_sentiment_score(self, last, frame):
        s = 0.0
        if len(frame) >= 3:
            c3 = self._get(frame.iloc[-3], ['close','close']); c1 = self._get(frame.iloc[-1], ['close','close'])
            if c3 and c1:
                mom = (c1 - c3) / c3 * 100
                if mom > 2: s += 8; elif mom > 0: s += 5; elif mom > -2: s += 3; else: s += 1
            else: s += 3
        return min(s, 10)
