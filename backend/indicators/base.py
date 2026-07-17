"""
Project: AlphaQuant AI
File: backend/indicators/base.py
Description: Technical indicator base classes and validation helpers.
Python Version: 3.11.9
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Indicator(ABC):
    """Abstract technical indicator."""

    name: str

    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate indicator values.

        Args:
            data: OHLCV dataframe.

        Returns:
            Dataframe containing indicator columns.
        """


def require_columns(data: pd.DataFrame, columns: set[str]) -> None:
    """
    Validate required dataframe columns.

    Args:
        data: Input dataframe.
        columns: Required column names.

    Raises:
        ValueError: If any required column is missing.
    """
    missing = columns.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

