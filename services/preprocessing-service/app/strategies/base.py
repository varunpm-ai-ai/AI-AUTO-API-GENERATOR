"""
Cleaning Strategy Interface (Strategy Pattern).
Defines standard contracts for pluggable, interchangeable data cleaning algorithms.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class ICleaningStrategy(ABC):
    """Abstract Strategy for executing a single data quality transformation."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the strategy."""
        pass

    @abstractmethod
    def apply(self, df: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """
        Executes cleaning transformation on the dataframe and returns the cleaned dataframe.
        """
        pass
