"""
Whitespace & String Sanitization Strategy.
Trims whitespace, strips non-printable/control characters, and normalizes column headers into clean snake_case.
"""
from typing import Dict, Any
import re
import pandas as pd
from app.strategies.base import ICleaningStrategy


class WhitespaceSanitizationStrategy(ICleaningStrategy):
    """Sanitizes text fields and normalizes column header formatting."""

    @property
    def name(self) -> str:
        return "whitespace_sanitization"

    @staticmethod
    def _to_snake_case(name: str) -> str:
        s = str(name).strip()
        s = re.sub(r"[^\w\s-]", "", s)
        s = re.sub(r"[\s-]+", "_", s)
        return s.lower()

    def apply(self, df: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        if df.empty:
            return df

        # 1. Normalize Column Headers to snake_case if enabled
        if options.get("normalize_column_names", True):
            df.columns = [self._to_snake_case(col) for col in df.columns]

        # 2. Sanitize string columns (trim whitespace, remove control chars)
        if options.get("sanitize_strings", True):
            string_cols = df.select_dtypes(include=["object", "string"]).columns
            for col in string_cols:
                # Strip leading/trailing whitespaces and unprintable ASCII control characters
                df[col] = df[col].astype(str).apply(
                    lambda v: re.sub(r"[\x00-\x1f\x7f-\x9f]", "", v.strip()) if v != "nan" else v
                )

        return df
