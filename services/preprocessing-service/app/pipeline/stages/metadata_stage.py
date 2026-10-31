"""
Metadata & Profiling Generation Stage.
Generates statistical profile, column summaries, inferred schema, and SHA-256 integrity checksum.
"""
import hashlib
from app.pipeline.stage import IPipelineStage
from app.core.context import PipelineContext
from app.config.logger import get_logger
import pandas as pd
import numpy as np

logger = get_logger(__name__)


class MetadataGenerationStage(IPipelineStage):
    """Stage 8: Synthesizes detailed structural and statistical profile of the cleaned dataset."""

    @property
    def name(self) -> str:
        return "metadata_generation"

    def execute(self, context: PipelineContext) -> None:
        df = context.current_dataframe
        if df is None:
            return

        column_stats = []
        for col in df.columns:
            series = df[col]
            null_count = int(series.isnull().sum())
            total_count = len(series)
            null_pct = round((null_count / total_count * 100), 2) if total_count > 0 else 0.0
            unique_count = int(series.nunique(dropna=True))

            min_val = None
            max_val = None
            mean_val = None

            if pd.api.types.is_numeric_dtype(series.dtype):
                valid_num = series.dropna()
                if not valid_num.empty:
                    min_val = float(valid_num.min())
                    max_val = float(valid_num.max())
                    mean_val = float(round(valid_num.mean(), 4))

            sample_vals = [str(v) for v in series.dropna().head(3).tolist()]

            column_stats.append({
                "name": col,
                "inferred_type": str(series.dtype),
                "total_count": total_count,
                "null_count": null_count,
                "null_percentage": null_pct,
                "unique_count": unique_count,
                "min": min_val,
                "max": max_val,
                "mean": mean_val,
                "sample_values": sample_vals
            })

        # Calculate memory footprint and checksum
        mem_usage = int(df.memory_usage(deep=True).sum())
        checksum = hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

        context.dataset_metadata = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "memory_usage_bytes": mem_usage,
            "checksum_sha256": checksum,
            "columns": column_stats,
            "schema": {col: str(df[col].dtype) for col in df.columns}
        }

        logger.info(f"Generated metadata profile with {len(column_stats)} column summaries")
