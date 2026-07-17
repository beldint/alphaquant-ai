"""
Project: AlphaQuant AI
File: backend/indicators/momentum.py
Description: Momentum indicators including RSI, KDJ, CCI, WR, ROC, PSY, MFI, and BIAS.
Python Version: 3.11.9
"""

from __future__ import annotations

import pandas as pd

from backend.indicators.base import Indicator, require_columns


class RSIIndicator(Indicator):
    """Relative strength index indicator."""

    name = "RSI"

    def __init__(self, window: int = 14) -> None:
        """Initialize RSI window."""
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI."""
        require_columns(data, {"close"})
        delta = data["close"].diff()
        gain = delta.clip(lower=0).rolling(window=self.window).mean()
        loss = (-delta.clip(upper=0)).rolling(window=self.window).mean()
        rs = gain / loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs))
        return pd.DataFrame({"rsi": rsi}, index=data.index)


class KDJIndicator(Indicator):
    """KDJ stochastic oscillator indicator."""

    name = "KDJ"

    def __init__(self, window: int = 9) -> None:
        """Initialize KDJ window."""
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate K, D, and J values."""
        require_columns(data, {"high", "low", "close"})
        low_min = data["low"].rolling(window=self.window).min()
        high_max = data["high"].rolling(window=self.window).max()
        rsv = (data["close"] - low_min) / (high_max - low_min).replace(0, pd.NA) * 100
        k = rsv.ewm(com=2, adjust=False).mean()
        d = k.ewm(com=2, adjust=False).mean()
        j = 3 * k - 2 * d
        return pd.DataFrame({"k": k, "d": d, "j": j}, index=data.index)


class CCIIndicator(Indicator):
    """Commodity channel index indicator."""

    name = "CCI"

    def __init__(self, window: int = 14) -> None:
        """Initialize CCI window."""
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate CCI."""
        require_columns(data, {"high", "low", "close"})
        typical_price = (data["high"] + data["low"] + data["close"]) / 3
        mean = typical_price.rolling(window=self.window).mean()
        deviation = (typical_price - mean).abs().rolling(window=self.window).mean()
        cci = (typical_price - mean) / (0.015 * deviation.replace(0, pd.NA))
        return pd.DataFrame({"cci": cci}, index=data.index)


class WilliamsRIndicator(Indicator):
    """Williams percent range indicator."""

    name = "WR"

    def __init__(self, window: int = 14) -> None:
        """Initialize WR window."""
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Williams percent range."""
        require_columns(data, {"high", "low", "close"})
        high_max = data["high"].rolling(window=self.window).max()
        low_min = data["low"].rolling(window=self.window).min()
        wr = (high_max - data["close"]) / (high_max - low_min).replace(0, pd.NA) * -100
        return pd.DataFrame({"wr": wr}, index=data.index)


class ROCIndicator(Indicator):
    """Rate of change indicator."""

    name = "ROC"

    def __init__(self, window: int = 12) -> None:
        """Initialize ROC window."""
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate ROC."""
        require_columns(data, {"close"})
        roc = data["close"].pct_change(periods=self.window) * 100
        return pd.DataFrame({"roc": roc}, index=data.index)


class PSYIndicator(Indicator):
    """Psychological line indicator."""

    name = "PSY"

    def __init__(self, window: int = 12) -> None:
        """Initialize PSY window."""
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate PSY."""
        require_columns(data, {"close"})
        up_days = (data["close"].diff() > 0).rolling(window=self.window).sum()
        psy = up_days / self.window * 100
        return pd.DataFrame({"psy": psy}, index=data.index)


class MFIIndicator(Indicator):
    """Money flow index indicator."""

    name = "MFI"

    def __init__(self, window: int = 14) -> None:
        """Initialize MFI window."""
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MFI."""
        require_columns(data, {"high", "low", "close", "volume"})
        typical_price = (data["high"] + data["low"] + data["close"]) / 3
        money_flow = typical_price * data["volume"]
        positive = money_flow.where(typical_price.diff() > 0, 0)
        negative = money_flow.where(typical_price.diff() < 0, 0)
        ratio = positive.rolling(self.window).sum() / negative.rolling(self.window).sum().replace(0, pd.NA)
        mfi = 100 - (100 / (1 + ratio))
        return pd.DataFrame({"mfi": mfi}, index=data.index)


class BIASIndicator(Indicator):
    """BIAS deviation indicator."""

    name = "BIAS"

    def __init__(self, windows: tuple[int, ...] = (6, 12, 24)) -> None:
        """Initialize BIAS windows."""
        self.windows = windows

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate BIAS values."""
        require_columns(data, {"close"})
        result = pd.DataFrame(index=data.index)
        for window in self.windows:
            average = data["close"].rolling(window=window).mean()
            result[f"bias_{window}"] = (data["close"] - average) / average * 100
        return result

