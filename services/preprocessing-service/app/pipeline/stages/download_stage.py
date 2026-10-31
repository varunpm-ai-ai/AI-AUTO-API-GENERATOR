"""
Download & Ingestion Stage.
Fetches the raw dataset from object storage or local path into the job's ephemeral scratch workspace.
"""
from pathlib import Path
from app.pipeline.stage import IPipelineStage
from app.core.context import PipelineContext
from app.storage.s3_client import storage_client
from app.config.logger import get_logger

logger = get_logger(__name__)


class DownloadStage(IPipelineStage):
    """Stage 1: Ingests raw data from remote storage into local scratch."""

    @property
    def name(self) -> str:
        return "download_ingestion"

    def execute(self, context: PipelineContext) -> None:
        if not context.scratch_dir:
            raise ValueError("Scratch directory must be allocated prior to downloading.")

        # Determine target filename
        source_name = Path(context.source_uri).name or "raw_dataset"
        destination_path = context.scratch_dir / f"raw_{source_name}"

        # Download from S3 or copy local
        downloaded_path = storage_client.download_file(context.source_uri, destination_path)
        context.local_raw_path = downloaded_path
        logger.info(f"Ingested raw dataset to {downloaded_path} ({downloaded_path.stat().st_size} bytes)")
