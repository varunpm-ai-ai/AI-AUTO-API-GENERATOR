"""
Null Imputation Cleaning Strategy.
Provides configurable handling of missing/null values (MEAN, MEDIAN, MODE, CONSTANT, or DROP).
"""
from typing import Dict, Any
import pandas as pd
import numpy as np
from app.strategies.base import ICleaningStrategy
from app.schemas.job import ImputationMethod
from app.config.logger import get_logger

logger = get_logger(__name__)


class NullImputationStrategy(ICleaningStrategy):
    """Fills or drops missing/null values based on configured policy."""

    @property
    def name(self) -> str:
        return "null_imputation"

    def apply(self, df: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        if df.empty:
            return df

        method_val = options.get("null_imputation", ImputationMethod.DROP)
        method = method_val.value if isinstance(method_val, ImputationMethod) else str(method_val).upper()

        if method == ImputationMethod.DROP.value:
            before = len(df)
            df = df.dropna(how="all")
            # If all rows were not completely null, drop rows with nulls in critical primary columns
            logger.debug(f"Dropped {before - len(df)} entirely null rows")
            return df

        if method == ImputationMethod.CONSTANT.value:
            constant_val = options.get("imputation_constant_value", "")
            return df.fillna(constant_val)

        # For statistical imputation, apply to numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                if method == ImputationMethod.MEAN.value:
                    mean_val = df[col].mean()
                    df[col] = df[col].fillna(mean_val)
                elif method == ImputationMethod.MEDIAN.value:
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                elif method == ImputationMethod.MODE.value:
                    mode_val = df[col].mode()
                    if not mode_val.empty:
                        df[col] = df[col].fillna(mode_val[0])

        # Fill any remaining object/string nulls with empty string
        object_cols = df.select_dtypes(include=["object", "string"]).columns
        for col in object_cols:
            df[col] = df[col].fillna("")

        return df
