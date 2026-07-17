"""
Project: AlphaQuant AI
File: backend/indicators/calculator.py
Description: Technical indicator calculator and default indicator registry.
Python Version: 3.11.9
"""

from __future__ import annotations

import pandas as pd
from loguru import logger

from backend.indicators.base import Indicator
from backend.indicators.momentum import (
    BIASIndicator,
    CCIIndicator,
    KDJIndicator,
    MFIIndicator,
    PSYIndicator,
    ROCIndicator,
    RSIIndicator,
    WilliamsRIndicator,
)
from backend.indicators.trend import (
    BollingerBandsIndicator,
    ExponentialMovingAverageIndicator,
    MACDIndicator,
    MovingAverageIndicator,
    TRIXIndicator,
)
from backend.indicators.volatility import ATRIndicator, DMIIndicator, SARIndicator
from backend.indicators.volume import OBVIndicator, VRIndicator, VolumeIndicator


class IndicatorCalculator:
    """Calculate a configured set of technical indicators."""

    def __init__(self, indicators: list[Indicator] | None = None) -> None:
        """Initialize calculator with indicators."""
        self.indicators = indicators or build_default_indicators()

    def calculate_all(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all configured indicators.

        Args:
            data: OHLCV dataframe with open, high, low, close, volume columns.

        Returns:
            Dataframe containing original data and indicator columns.
        """
        result = data.copy()
        for indicator in self.indicators:
            try:
                indicator_frame = indicator.calculate(data)
                result = result.join(indicator_frame)
            except ValueError as exc:
                logger.warning(
                    "Indicator skipped: name={name} error={error}",
                    name=indicator.name,
                    error=str(exc),
                )
        return result


def build_default_indicators() -> list[Indicator]:
    """
    Build the default production indicator set.

    Returns:
        List of indicator instances.
    """
    return [
        MovingAverageIndicator(),
        ExponentialMovingAverageIndicator(),
        MACDIndicator(),
        KDJIndicator(),
        RSIIndicator(),
        BollingerBandsIndicator(),
        ATRIndicator(),
        CCIIndicator(),
        OBVIndicator(),
        VolumeIndicator(),
        DMIIndicator(),
        WilliamsRIndicator(),
        SARIndicator(),
        ROCIndicator(),
        TRIXIndicator(),
        PSYIndicator(),
        MFIIndicator(),
        VRIndicator(),
        BIASIndicator(),
    ]

