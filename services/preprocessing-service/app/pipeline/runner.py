"""
Pipeline Runner (Chain of Responsibility / Pipeline Pattern Orchestrator).
Sequentially executes registered IPipelineStage instances and tracks execution telemetry.
"""
from typing import List, Optional
import time
from app.pipeline.stage import IPipelineStage
from app.core.context import PipelineContext
from app.core.exceptions import ProcessingTimeoutError
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)


class PipelineRunner:
    """Orchestrates sequential execution of pipeline stages."""

    def __init__(self, stages: Optional[List[IPipelineStage]] = None):
        self.stages: List[IPipelineStage] = stages or []

    def add_stage(self, stage: IPipelineStage) -> "PipelineRunner":
        """Appends a stage to the pipeline chain."""
        self.stages.append(stage)
        return self

    def execute(self, context: PipelineContext) -> None:
        """
        Executes all stages in sequence against the provided context.
        Enforces cancellation and timeout boundaries.
        """
        timeout_seconds = settings.PROCESSING_TIMEOUT_SECONDS
        logger.info(f"Starting pipeline execution with {len(self.stages)} stages for job {context.job_id}")

        for index, stage in enumerate(self.stages):
            if context.is_cancelled:
                logger.warning(f"Pipeline execution aborted: job {context.job_id} was cancelled")
                return

            # Check timeout deadline
            elapsed_seconds = (time.time() - context.start_time)
            if elapsed_seconds > timeout_seconds:
                raise ProcessingTimeoutError(
                    f"Job {context.job_id} exceeded deadline timeout of {timeout_seconds}s at stage '{stage.name}'"
                )

            stage_start = time.time()
            logger.debug(f"Executing stage [{index + 1}/{len(self.stages)}]: {stage.name}")

            try:
                stage.execute(context)
                duration_ms = (time.time() - stage_start) * 1000.0
                context.record_stage_metric(stage.name, duration_ms, status="SUCCESS")
                logger.debug(f"Stage '{stage.name}' finished in {duration_ms:.2f}ms")

            except Exception as e:
                duration_ms = (time.time() - stage_start) * 1000.0
                context.record_stage_metric(stage.name, duration_ms, status="FAILED", details={"error": str(e)})
                logger.error(f"Stage '{stage.name}' failed after {duration_ms:.2f}ms: {e}", exc_info=True)
                raise
