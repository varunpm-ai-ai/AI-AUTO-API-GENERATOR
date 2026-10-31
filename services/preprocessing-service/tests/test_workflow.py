"""
Integration Tests for Command and Template Method Patterns.
"""
from app.schemas.job import JobRequestPayload, JobStatus
from app.commands.preprocess_command import PreprocessingJobCommand
from app.workflows.standard_workflow import StandardPreprocessingWorkflow


def test_command_execution_end_to_end(sample_csv_path):
    payload = JobRequestPayload(
        job_id="job-cmd-test-100",
        dataset_id="ds-cmd-100",
        source_uri=f"file://{sample_csv_path.resolve()}",
        format_hint="csv"
    )

    command = PreprocessingJobCommand(payload)
    assert command.get_status() == JobStatus.PENDING

    result = command.execute()

    assert result.status == JobStatus.COMPLETED
    assert result.job_id == "job-cmd-test-100"
    assert result.row_count > 0
    assert result.processed_uri is not None
    assert command.get_status() == JobStatus.COMPLETED


def test_duplicate_job_idempotency(sample_csv_path):
    payload = JobRequestPayload(
        job_id="job-idempotency-key-200",
        dataset_id="ds-idemp-200",
        source_uri=f"file://{sample_csv_path.resolve()}"
    )

    # First execution succeeds
    cmd1 = PreprocessingJobCommand(payload)
    res1 = cmd1.execute()
    assert res1.status == JobStatus.COMPLETED

    # Second execution with same job_id is detected as duplicate and returns immediately
    cmd2 = PreprocessingJobCommand(payload)
    res2 = cmd2.execute()
    assert res2.status == JobStatus.COMPLETED
    assert "Duplicate execution detected" in (res2.error_message or "")
