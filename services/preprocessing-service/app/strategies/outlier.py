"""
Outlier Detection & Clamping Strategy.
Uses the Interquartile Range (IQR) technique to detect and clamp extreme numeric anomalies.
"""
from typing import Dict, Any
import pandas as pd
import numpy as np
from app.strategies.base import ICleaningStrategy


class OutlierStrategy(ICleaningStrategy):
    """Detects and clamps numerical outliers based on IQR boundaries."""

    @property
    def name(self) -> str:
        return "outlier_handling"

    def apply(self, df: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        if df.empty or not options.get("handle_outliers", False):
            return df

        iqr_mult = options.get("outlier_threshold_iqr", 1.5)
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_fence = q1 - (iqr_mult * iqr)
            upper_fence = q3 + (iqr_mult * iqr)

            # Clamp values to the fences
            df[col] = df[col].clip(lower=lower_fence, upper=upper_fence)

        return df
