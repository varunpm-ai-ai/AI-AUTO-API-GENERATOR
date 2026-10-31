"""
Preprocessing Job Command (Command Pattern).
Encapsulates all execution parameters, idempotency checks, workflow invocation, and cancellation state.
"""
from typing import Optional
from app.commands.base import IJobCommand
from app.schemas.job import JobRequestPayload, JobResultResponse, JobStatus
from app.workflows.base import BasePreprocessingWorkflow
from app.workflows.standard_workflow import StandardPreprocessingWorkflow
from app.messaging.idempotency import idempotency_guard
from app.core.exceptions import DuplicateJobError
from app.config.logger import get_logger

logger = get_logger(__name__)


class PreprocessingJobCommand(IJobCommand):
    """
    Concrete Command encapsulating the preprocessing job execution contract.
    """

    def __init__(
        self,
        payload: JobRequestPayload,
        workflow: Optional[BasePreprocessingWorkflow] = None
    ):
        self.payload = payload
        self.workflow = workflow or StandardPreprocessingWorkflow()
        self.status = JobStatus.PENDING
        self.cancellation_reason: Optional[str] = None
        self._is_aborted = False

    def execute(self) -> JobResultResponse:
        """
        Executes the preprocessing job command.
        1. Checks and acquires idempotency lock.
        2. Sets state to PROCESSING.
        3. Invokes the workflow.
        4. Updates status.
        """
        job_id = self.payload.job_id

        # 1. Check idempotency lock
        if not idempotency_guard.acquire_lock(job_id):
            logger.warning(f"Job {job_id} is already in progress or already completed. Skipping redundant execution.")
            return JobResultResponse(
                job_id=job_id,
                dataset_id=self.payload.dataset_id,
                status=JobStatus.COMPLETED,
                error_message="Duplicate execution detected; job is already processed or currently active."
            )

        self.status = JobStatus.PROCESSING
        logger.info(f"Executing PreprocessingJobCommand for job {job_id}")

        # 2. Invoke workflow template
        result = self.workflow.run(self.payload)
        self.status = result.status
        return result

    def abort(self, reason: str) -> None:
        """Signals cancellation to the running job command."""
        self._is_aborted = True
        self.cancellation_reason = reason
        self.status = JobStatus.CANCELLED
        idempotency_guard.release_lock(self.payload.job_id)
        logger.warning(f"Job {self.payload.job_id} was aborted: {reason}")

    def get_status(self) -> JobStatus:
        """Returns the current execution status."""
        return self.status
