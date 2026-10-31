"""
Base Preprocessing Workflow (Template Method Pattern).
Defines the invariant skeleton of a preprocessing workflow with customizable hook steps.
"""
from abc import ABC, abstractmethod
import time
from app.core.context import PipelineContext
from app.schemas.job import JobRequestPayload, JobResultResponse, JobStatus
from app.storage.scratch import ScratchDirectoryManager
from app.config.logger import get_logger, correlation_id_ctx

logger = get_logger(__name__)


class BasePreprocessingWorkflow(ABC):
    """
    Template Method Pattern: Invariant workflow algorithm skeleton.
    Subclasses customize specific lifecycle behaviors or pipeline compositions.
    """

    def run(self, payload: JobRequestPayload) -> JobResultResponse:
        """
        The Template Method. Defines the unchangeable order of steps:
        1. Context Initialization
        2. Hook: before_execute
        3. Execute processing stages
        4. Hook: after_execute
        5. Build result contract
        6. Exception Handling / on_error Hook
        7. Guaranteed Ephemeral Scratch Cleanup
        """
        # Set correlation context for tracing
        token = correlation_id_ctx.set(payload.correlation_id)
        scratch_mgr = ScratchDirectoryManager(job_id=payload.job_id)
        context = PipelineContext(
            job_id=payload.job_id,
            dataset_id=payload.dataset_id,
            correlation_id=payload.correlation_id,
            source_uri=payload.source_uri,
            cleaning_config=payload.cleaning_options.model_dump()
        )

        try:
            # Step 1: Allocate scratch workspace
            context.scratch_dir = scratch_mgr.create()

            # Step 2: Hook before execution
            self.before_execute(context)

            # Step 3: Execute core pipeline stages
            self.execute_pipeline(context)

            # Step 4: Hook after execution
            self.after_execute(context)

            # Step 5: Build final success result
            result = self.build_success_result(context)
            logger.info(
                f"Job {payload.job_id} successfully completed in {result.duration_ms:.2f}ms "
                f"({result.row_count} rows, {result.column_count} columns)"
            )
            return result

        except Exception as error:
            logger.error(f"Job {payload.job_id} encountered fatal error: {error}", exc_info=True)
            self.on_error(context, error)
            return self.build_failure_result(context, error)

        finally:
            # Step 7: Deterministic cleanup
            scratch_mgr.cleanup()
            correlation_id_ctx.reset(token)

    def before_execute(self, context: PipelineContext) -> None:
        """Hook called immediately before pipeline stages run."""
        pass

    @abstractmethod
    def execute_pipeline(self, context: PipelineContext) -> None:
        """Abstract method where subclasses invoke their specific PipelineRunner."""
        pass

    def after_execute(self, context: PipelineContext) -> None:
        """Hook called immediately after pipeline stages successfully conclude."""
        pass

    def on_error(self, context: PipelineContext, error: Exception) -> None:
        """Hook called when any stage raises an exception."""
        pass

    def build_success_result(self, context: PipelineContext) -> JobResultResponse:
        """Constructs the standard JobResultResponse on success."""
        df = context.current_dataframe
        row_count = len(df) if df is not None else 0
        column_count = len(df.columns) if df is not None else 0
        schema_def = {col: str(df[col].dtype) for col in df.columns} if df is not None else {}

        return JobResultResponse(
            job_id=context.job_id,
            dataset_id=context.dataset_id,
            status=JobStatus.COMPLETED,
            processed_uri=context.output_s3_uri,
            row_count=row_count,
            column_count=column_count,
            detected_format=context.detected_format,
            schema_definition=schema_def,
            metadata=context.dataset_metadata,
            validation_report=context.validation_report,
            duration_ms=round(context.get_total_duration_ms(), 2)
        )

    def build_failure_result(self, context: PipelineContext, error: Exception) -> JobResultResponse:
        """Constructs the standard JobResultResponse on failure."""
        return JobResultResponse(
            job_id=context.job_id,
            dataset_id=context.dataset_id,
            status=JobStatus.FAILED,
            processed_uri=None,
            row_count=0,
            column_count=0,
            detected_format=context.detected_format,
            duration_ms=round(context.get_total_duration_ms(), 2),
            error_message=str(error)
        )
