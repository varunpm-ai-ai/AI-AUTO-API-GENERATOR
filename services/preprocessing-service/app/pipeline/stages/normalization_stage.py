"""
Schema & Data Normalization Stage.
Standardizes character encoding to UTF-8, trims column headers, and infers consistent data types.
"""
from app.pipeline.stage import IPipelineStage
from app.core.context import PipelineContext
from app.config.logger import get_logger
import pandas as pd
import re

logger = get_logger(__name__)


class NormalizationStage(IPipelineStage):
    """Stage 5: Normalizes column names, casing, and standardizes data types."""

    @property
    def name(self) -> str:
        return "schema_normalization"

    def execute(self, context: PipelineContext) -> None:
        df = context.current_dataframe
        if df is None or df.empty:
            return

        # 1. Clean and normalize column names (remove special characters, trim, lower snake_case)
        normalized_cols = []
        for col in df.columns:
            clean_col = str(col).strip()
            clean_col = re.sub(r"[^\w\s-]", "", clean_col)
            clean_col = re.sub(r"[\s-]+", "_", clean_col).lower()
            normalized_cols.append(clean_col or f"col_{len(normalized_cols)}")
        df.columns = normalized_cols

        # 2. Attempt smart datetime inference for string columns matching standard ISO-8601
        for col in df.select_dtypes(include=["object", "string"]).columns:
            sample = df[col].dropna().head(20)
            if not sample.empty and sample.astype(str).str.match(r"^\d{4}-\d{2}-\d{2}").all():
                try:
                    df[col] = pd.to_datetime(df[col], errors="ignore")
                except Exception:
                    pass

        context.current_dataframe = df
        logger.info(f"Normalized schema for {len(df.columns)} columns")
