"""
Data Cleaning Stage (Strategy Runner).
Orchestrates interchangeable ICleaningStrategy implementations against the active DataFrame.
"""
from typing import List
from app.pipeline.stage import IPipelineStage
from app.core.context import PipelineContext
from app.strategies.base import ICleaningStrategy
from app.strategies.deduplication import DeduplicationStrategy
from app.strategies.imputation import NullImputationStrategy
from app.strategies.sanitization import WhitespaceSanitizationStrategy
from app.strategies.outlier import OutlierStrategy
from app.config.logger import get_logger

logger = get_logger(__name__)


class CleaningStage(IPipelineStage):
    """Stage 6: Executes data cleaning strategies."""

    def __init__(self, strategies: List[ICleaningStrategy] = None):
        self.strategies = strategies or [
            WhitespaceSanitizationStrategy(),
            DeduplicationStrategy(),
            NullImputationStrategy(),
            OutlierStrategy()
        ]

    @property
    def name(self) -> str:
        return "data_cleaning"

    def execute(self, context: PipelineContext) -> None:
        df = context.current_dataframe
        if df is None or df.empty:
            return

        options = context.cleaning_config or {}
        for strategy in self.strategies:
            logger.debug(f"Applying cleaning strategy: {strategy.name}")
            df = strategy.apply(df, options)

        context.current_dataframe = df
        logger.info(f"Completed cleaning transformations. Active row count: {len(df)}")
