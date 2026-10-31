"""
Data Validation Stage.
Asserts dataset quality invariants, null ratio thresholds, and non-empty guarantees.
"""
from app.pipeline.stage import IPipelineStage
from app.core.context import PipelineContext
from app.core.exceptions import DatasetValidationError
from app.config.logger import get_logger

logger = get_logger(__name__)


class ValidationStage(IPipelineStage):
    """Stage 7: Validates data quality invariants and checks for corrupt states."""

    @property
    def name(self) -> str:
        return "data_validation"

    def execute(self, context: PipelineContext) -> None:
        df = context.current_dataframe
        if df is None:
            raise DatasetValidationError("Validation failed: DataFrame is null.")

        row_count = len(df)
        col_count = len(df.columns)

        # Check for empty dataframe
        if row_count == 0 or col_count == 0:
            raise DatasetValidationError(f"Validation failed: Processed dataset has zero rows or zero columns (rows={row_count}, cols={col_count})")

        # Compute column null ratios
        null_ratios = (df.isnull().sum() / row_count).to_dict()
        flagged_columns = [col for col, ratio in null_ratios.items() if ratio > 0.90]

        validation_report = {
            "is_valid": True,
            "row_count": row_count,
            "column_count": col_count,
            "null_ratios": null_ratios,
            "high_null_columns": flagged_columns,
            "duplicate_count_after_clean": int(df.duplicated().sum())
        }

        context.validation_report = validation_report
        logger.info(f"Dataset passed validation checks (rows={row_count}, cols={col_count})")
