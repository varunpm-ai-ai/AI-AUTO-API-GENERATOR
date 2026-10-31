"""
Deduplication Cleaning Strategy.
Removes duplicate rows based on all or specified subset columns.
"""
from typing import Dict, Any, List
import pandas as pd
from app.strategies.base import ICleaningStrategy
from app.config.logger import get_logger

logger = get_logger(__name__)


class DeduplicationStrategy(ICleaningStrategy):
    """Removes duplicate rows from the dataset."""

    @property
    def name(self) -> str:
        return "deduplication"

    def apply(self, df: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        if df.empty:
            return df

        subset: List[str] = options.get("dedup_subset_columns")
        if subset:
            # Filter subset columns that actually exist in the dataframe
            valid_subset = [c for c in subset if c in df.columns]
            if valid_subset:
                before = len(df)
                df = df.drop_duplicates(subset=valid_subset, keep="first")
                logger.debug(f"Deduplicated by subset {valid_subset}: dropped {before - len(df)} rows")
                return df

        before = len(df)
        df = df.drop_duplicates(keep="first")
        dropped = before - len(df)
        if dropped > 0:
            logger.info(f"Deduplication dropped {dropped} duplicate rows")
        return df
