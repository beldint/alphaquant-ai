"""
Project: AlphaQuant AI
File: backend/indicators/volume.py
Description: Volume indicators including OBV, VOL, and VR.
Python Version: 3.11.9
"""

from __future__ import annotations

import pandas as pd

from backend.indicators.base import Indicator, require_columns


class OBVIndicator(Indicator):
    """On-balance volume indicator."""

    name = "OBV"

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate OBV."""
        require_columns(data, {"close", "volume"})
        direction = data["close"].diff().apply(lambda value: 1 if value > 0 else -1 if value < 0 else 0)
        obv = (direction * data["volume"]).fillna(0).cumsum()
        return pd.DataFrame({"obv": obv}, index=data.index)


class VolumeIndicator(Indicator):
    """Volume moving average indicator."""

    name = "VOL"

    def __init__(self, windows: tuple[int, ...] = (5, 10, 20)) -> None:
        """Initialize volume moving average windows."""
        self.windows = windows

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume averages."""
        require_columns(data, {"volume"})
        result = pd.DataFrame({"volume": data["volume"]}, index=data.index)
        for window in self.windows:
            result[f"vol_ma_{window}"] = data["volume"].rolling(window=window).mean()
        return result


class VRIndicator(Indicator):
    """Volume ratio indicator."""

    name = "VR"

    def __init__(self, window: int = 24) -> None:
        """Initialize VR window."""
        self.window = window

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate VR."""
        require_columns(data, {"close", "volume"})
        change = data["close"].diff()
        up_volume = data["volume"].where(change > 0, 0).rolling(self.window).sum()
        down_volume = data["volume"].where(change < 0, 0).rolling(self.window).sum()
        flat_volume = data["volume"].where(change == 0, 0).rolling(self.window).sum()
        vr = (up_volume + flat_volume / 2) / (down_volume + flat_volume / 2).replace(0, pd.NA) * 100
        return pd.DataFrame({"vr": vr}, index=data.index)

