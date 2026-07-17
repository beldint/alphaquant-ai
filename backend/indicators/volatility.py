"""
Project: AlphaQuant AI
File: backend/indicators/volatility.py
Description: Volatility and trend strength indicators including ATR, DMI, and SAR.
Python Version: 3.11.9
"""

from __future__ import annotations

import pandas as pd

from backend.indicators.base import Indicator, require_columns


class ATRIndicator(Indicator):
    """Average true range indicator."""

    name = "ATR"

    def __init__(self, window: int = 14) -> None:
        """Initialize ATR window."""
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate ATR."""
        require_columns(data, {"high", "low", "close"})
        previous_close = data["close"].shift(1)
        true_range = pd.concat(
            [
                data["high"] - data["low"],
                (data["high"] - previous_close).abs(),
                (data["low"] - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr = true_range.rolling(window=self.window).mean()
        return pd.DataFrame({"atr": atr}, index=data.index)


class DMIIndicator(Indicator):
    """Directional movement index indicator."""

    name = "DMI"

    def __init__(self, window: int = 14) -> None:
        """Initialize DMI window."""
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate PDI, MDI, ADX, and ADXR."""
        require_columns(data, {"high", "low", "close"})
        high_diff = data["high"].diff()
        low_diff = -data["low"].diff()
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        atr = ATRIndicator(self.window).calculate(data)["atr"].replace(0, pd.NA)
        pdi = 100 * plus_dm.rolling(self.window).sum() / atr
        mdi = 100 * minus_dm.rolling(self.window).sum() / atr
        dx = ((pdi - mdi).abs() / (pdi + mdi).replace(0, pd.NA)) * 100
        adx = dx.rolling(self.window).mean()
        adxr = (adx + adx.shift(self.window)) / 2
        return pd.DataFrame({"pdi": pdi, "mdi": mdi, "adx": adx, "adxr": adxr}, index=data.index)


class SARIndicator(Indicator):
    """Parabolic SAR indicator."""

    name = "SAR"

    def __init__(self, step: float = 0.02, max_step: float = 0.2) -> None:
        """Initialize SAR parameters."""
        self.step = step
        self.max_step = max_step

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate parabolic SAR."""
        require_columns(data, {"high", "low"})
        if data.empty:
            return pd.DataFrame({"sar": []}, index=data.index)

        high = data["high"].reset_index(drop=True)
        low = data["low"].reset_index(drop=True)
        sar_values = [float(low.iloc[0])]
        is_rising = True
        extreme_point = float(high.iloc[0])
        acceleration = self.step

        for index in range(1, len(data)):
            previous_sar = sar_values[-1]
            current_sar = previous_sar + acceleration * (extreme_point - previous_sar)
            if is_rising:
                if low.iloc[index] < current_sar:
                    is_rising = False
                    current_sar = extreme_point
                    extreme_point = float(low.iloc[index])
                    acceleration = self.step
                elif high.iloc[index] > extreme_point:
                    extreme_point = float(high.iloc[index])
                    acceleration = min(acceleration + self.step, self.max_step)
            elif high.iloc[index] > current_sar:
                is_rising = True
                current_sar = extreme_point
                extreme_point = float(high.iloc[index])
                acceleration = self.step
            elif low.iloc[index] < extreme_point:
                extreme_point = float(low.iloc[index])
                acceleration = min(acceleration + self.step, self.max_step)
            sar_values.append(current_sar)

        return pd.DataFrame({"sar": sar_values}, index=data.index)

