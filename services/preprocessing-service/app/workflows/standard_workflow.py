"""
Standard Preprocessing Workflow Implementation.
Concrete implementation of BasePreprocessingWorkflow configuring the 9 standard processing stages.
"""
from typing import Optional
from app.workflows.base import BasePreprocessingWorkflow
from app.pipeline.runner import PipelineRunner
from app.core.context import PipelineContext
from app.pipeline.stages import (
    DownloadStage,
    DetectionStage,
    ExtractionStage,
    ParsingStage,
    NormalizationStage,
    CleaningStage,
    ValidationStage,
    MetadataGenerationStage,
    StorageStage
)
from app.messaging.idempotency import idempotency_guard
from app.config.logger import get_logger

logger = get_logger(__name__)


class StandardPreprocessingWorkflow(BasePreprocessingWorkflow):
    """
    Standard tabular/document preprocessing workflow composing all 9 core stages.
    """

    def __init__(self, runner: Optional[PipelineRunner] = None):
        if runner:
            self.runner = runner
        else:
            self.runner = PipelineRunner([
                DownloadStage(),
                DetectionStage(),
                ExtractionStage(),
                ParsingStage(),
                NormalizationStage(),
                CleaningStage(),
                ValidationStage(),
                MetadataGenerationStage(),
                StorageStage()
            ])

    def before_execute(self, context: PipelineContext) -> None:
        logger.info(f"Initialized Standard Workflow for job {context.job_id} on dataset {context.dataset_id}")

    def execute_pipeline(self, context: PipelineContext) -> None:
        """Executes the pipeline runner chain."""
        self.runner.execute(context)

    def after_execute(self, context: PipelineContext) -> None:
        """Marks idempotency lock as COMPLETED upon successful pipeline completion."""
        idempotency_guard.mark_completed(context.job_id)
        logger.info(f"Workflow finished all stages successfully for job {context.job_id}")

    def on_error(self, context: PipelineContext, error: Exception) -> None:
        """Releases the idempotency lock to permit retries after failure."""
        idempotency_guard.release_lock(context.job_id)
        logger.warning(f"Workflow failed for job {context.job_id}: {error}. Released idempotency lock.")
