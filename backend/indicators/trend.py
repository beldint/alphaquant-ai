"""
Project: AlphaQuant AI
File: backend/indicators/trend.py
Description: Trend technical indicators including MA, EMA, MACD, BOLL, and TRIX.
Python Version: 3.11.9
"""

from __future__ import annotations

import pandas as pd

from backend.indicators.base import Indicator, require_columns


class MovingAverageIndicator(Indicator):
    """Simple moving average indicator."""

    name = "MA"

    def __init__(self, windows: tuple[int, ...] = (5, 10, 20, 60)) -> None:
        """Initialize moving average windows."""
        self.windows = windows

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages."""
        require_columns(data, {"close"})
        result = pd.DataFrame(index=data.index)
        for window in self.windows:
            result[f"ma_{window}"] = data["close"].rolling(window=window).mean()
        return result


class ExponentialMovingAverageIndicator(Indicator):
    """Exponential moving average indicator."""

    name = "EMA"

    def __init__(self, windows: tuple[int, ...] = (12, 26)) -> None:
        """Initialize exponential moving average windows."""
        self.windows = windows

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate exponential moving averages."""
        require_columns(data, {"close"})
        result = pd.DataFrame(index=data.index)
        for window in self.windows:
            result[f"ema_{window}"] = data["close"].ewm(span=window, adjust=False).mean()
        return result


class MACDIndicator(Indicator):
    """Moving average convergence divergence indicator."""

    name = "MACD"

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9) -> None:
        """Initialize MACD parameters."""
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate DIF, DEA, and MACD histogram."""
        require_columns(data, {"close"})
        ema_fast = data["close"].ewm(span=self.fast, adjust=False).mean()
        ema_slow = data["close"].ewm(span=self.slow, adjust=False).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=self.signal, adjust=False).mean()
        macd = (dif - dea) * 2
        return pd.DataFrame({"dif": dif, "dea": dea, "macd": macd}, index=data.index)


class BollingerBandsIndicator(Indicator):
    """Bollinger Bands indicator."""

    name = "BOLL"

    def __init__(self, window: int = 20, std_multiplier: float = 2.0) -> None:
        """Initialize Bollinger Bands parameters."""
        self.window = window
        self.std_multiplier = std_multiplier

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger middle, upper, and lower bands."""
        require_columns(data, {"close"})
        middle = data["close"].rolling(window=self.window).mean()
        std = data["close"].rolling(window=self.window).std()
        upper = middle + self.std_multiplier * std
        lower = middle - self.std_multiplier * std
        return pd.DataFrame(
            {"boll_mid": middle, "boll_upper": upper, "boll_lower": lower},
            index=data.index,
        )


class TRIXIndicator(Indicator):
    """Triple exponential average momentum indicator."""

    name = "TRIX"

    def __init__(self, window: int = 12, signal: int = 9) -> None:
        """Initialize TRIX parameters."""
        self.window = window
        self.signal = signal

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate TRIX and signal matrix."""
        require_columns(data, {"close"})
        ema1 = data["close"].ewm(span=self.window, adjust=False).mean()
        ema2 = ema1.ewm(span=self.window, adjust=False).mean()
        ema3 = ema2.ewm(span=self.window, adjust=False).mean()
        trix = ema3.pct_change() * 100
        matrix = trix.rolling(window=self.signal).mean()
        return pd.DataFrame({"trix": trix, "trix_matrix": matrix}, index=data.index)

