"""
Unit & Integration Tests for Pipeline Stages and PipelineRunner (Pipeline Pattern).
"""
import pytest
from app.core.context import PipelineContext
from app.pipeline.runner import PipelineRunner
from app.pipeline.stages import (
    DetectionStage,
    ParsingStage,
    NormalizationStage,
    CleaningStage,
    ValidationStage,
    MetadataGenerationStage
)


def test_pipeline_stages_execution(sample_csv_path, temp_dir):
    context = PipelineContext(
        job_id="test-job-1",
        dataset_id="test-ds-1",
        correlation_id="corr-123",
        source_uri=str(sample_csv_path),
        local_raw_path=sample_csv_path,
        scratch_dir=temp_dir,
        cleaning_config={"deduplicate": True, "sanitize_strings": True}
    )

    runner = PipelineRunner([
        DetectionStage(),
        ParsingStage(),
        NormalizationStage(),
        CleaningStage(),
        ValidationStage(),
        MetadataGenerationStage()
    ])

    runner.execute(context)

    # Assert Detection
    assert context.detected_format in ["csv", "tsv"]

    # Assert Parsing & Cleaning
    assert context.current_dataframe is not None
    # 4 rows original with 1 duplicate -> 3 rows after clean
    assert len(context.current_dataframe) == 3

    # Assert Validation & Metadata
    assert context.validation_report["is_valid"] is True
    assert "checksum_sha256" in context.dataset_metadata
    assert context.dataset_metadata["row_count"] == 3
    assert len(context.stage_metrics) == 6
