"""
Storage & Persistence Stage.
Persists the final standardized dataset as compressed Apache Parquet in Object Storage.
"""
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import json
from app.pipeline.stage import IPipelineStage
from app.core.context import PipelineContext
from app.storage.s3_client import storage_client
from app.config.logger import get_logger

logger = get_logger(__name__)


class StorageStage(IPipelineStage):
    """Stage 9: Writes compressed Parquet artifact and uploads to S3/MinIO."""

    @property
    def name(self) -> str:
        return "storage_persistence"

    def execute(self, context: PipelineContext) -> None:
        df = context.current_dataframe
        if df is None:
            raise ValueError("No DataFrame available to persist.")

        # 1. Write clean Parquet locally inside scratch directory
        parquet_filename = f"dataset_{context.dataset_id}.parquet"
        local_parquet_path = context.scratch_dir / parquet_filename
        context.local_processed_path = local_parquet_path

        # Write Parquet with Snappy compression
        table = pa.Table.from_pandas(df)
        pq.write_table(table, str(local_parquet_path), compression="snappy")

        # 2. Write sidecar metadata JSON
        metadata_filename = f"dataset_{context.dataset_id}_metadata.json"
        local_meta_path = context.scratch_dir / metadata_filename
        with open(local_meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "job_id": context.job_id,
                "dataset_id": context.dataset_id,
                "metadata": context.dataset_metadata,
                "validation": context.validation_report
            }, f, indent=2)

        # 3. Upload to object storage
        s3_object_key = f"datasets/{context.dataset_id}/{parquet_filename}"
        s3_uri = storage_client.upload_file(local_parquet_path, s3_object_key)
        context.output_s3_uri = s3_uri

        # Also upload sidecar metadata
        meta_s3_key = f"datasets/{context.dataset_id}/{metadata_filename}"
        storage_client.upload_file(local_meta_path, meta_s3_key)

        logger.info(f"Persisted standardized dataset to {s3_uri}")
