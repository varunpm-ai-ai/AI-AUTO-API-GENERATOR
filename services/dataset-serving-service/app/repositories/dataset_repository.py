"""
Dataset Repository Implementation.
Orchestrates S3 storage retrieval and DuckDB analytical querying.
"""
from typing import List, Tuple, Iterator, Optional
from datetime import datetime, timezone
from pathlib import Path
import pyarrow as pa
import hashlib
from app.repositories.base import IDatasetRepository
from app.schemas.dataset import (
    DatasetMetadataResponse,
    DatasetSchemaResponse,
    DatasetColumnSchema,
    ColumnProfileStat,
    DatasetVersionsResponse,
    DatasetVersionItem,
    DatasetSearchResultItem,
    DatasetStatusResponse,
    DatasetStatus
)
from app.builders.query_builder import QuerySpecification
from app.storage.s3_reader import storage_reader
from app.engines.factory import AnalyticalEngineFactory
from app.strategies.factory import ExportStrategyFactory
from app.grpc_client.catalog_client import catalog_grpc_client
from app.core.exceptions import DatasetNotFoundError
from app.config.logger import get_logger

logger = get_logger(__name__)


class DatasetRepository(IDatasetRepository):
    """Core repository executing Parquet operations via DuckDB and S3."""

    def __init__(self):
        self.engine = AnalyticalEngineFactory.get_engine()
        self.storage = storage_reader
        self.catalog_grpc = catalog_grpc_client

    def search_datasets(self, query: Optional[str] = None, format_code: Optional[str] = None) -> List[DatasetSearchResultItem]:
        # 1. Attempt gRPC query to Catalog Service
        grpc_res = self.catalog_grpc.list_datasets(page=1, limit=50)
        if grpc_res and grpc_res.datasets:
            results = []
            for d in grpc_res.datasets:
                if not query or query.lower() in d.name.lower() or query.lower() in d.dataset_id.lower():
                    results.append(DatasetSearchResultItem(
                        dataset_id=d.dataset_id,
                        name=d.name,
                        description=d.description or "Registered dataset in catalog",
                        status=DatasetStatus.SERVING,
                        version="latest",
                        format="parquet"
                    ))
            if results:
                return results

        # 2. Fallback to search available local/cached datasets
        results = []
        cache_base = Path("./tmp/serving_cache")
        if cache_base.exists():
            for ds_dir in cache_base.iterdir():
                if ds_dir.is_dir():
                    ds_id = ds_dir.name
                    if not query or query.lower() in ds_id.lower():
                        results.append(DatasetSearchResultItem(
                            dataset_id=ds_id,
                            name=f"Dataset {ds_id}",
                            description="Processed standardized tabular dataset",
                            status=DatasetStatus.SERVING,
                            version="latest",
                            format="parquet"
                        ))
        return results

    def get_metadata(self, dataset_id: str, version: str = "latest") -> DatasetMetadataResponse:
        try:
            parquet_path = self.storage.resolve_dataset_local_path(dataset_id, version)
        except Exception as e:
            raise DatasetNotFoundError(f"Dataset '{dataset_id}' not found: {e}")

        schema = self.engine.get_schema(str(parquet_path))
        total_rows = self.engine.get_row_count(str(parquet_path))
        file_size = parquet_path.stat().st_size

        # Attempt to enrich from gRPC catalog details
        catalog_detail = self.catalog_grpc.get_dataset(dataset_id)
        dataset_name = catalog_detail.name if catalog_detail else f"Dataset {dataset_id}"

        column_stats = [
            ColumnProfileStat(
                name=field.name,
                inferred_type=str(field.type),
                null_count=0,
                unique_count=0
            ) for field in schema
        ]

        return DatasetMetadataResponse(
            dataset_id=dataset_id,
            version=version,
            status=DatasetStatus.SERVING,
            row_count=total_rows,
            column_count=len(schema),
            memory_usage_bytes=file_size,
            checksum_sha256=hashlib.sha256(str(parquet_path).encode("utf-8")).hexdigest()[:16],
            storage_uri=f"s3://processed-data/datasets/{dataset_id}/dataset_{dataset_id}.parquet",
            columns=column_stats,
            created_at=catalog_detail.created_at if catalog_detail else datetime.now(timezone.utc).isoformat()
        )

    def get_schema(self, dataset_id: str, version: str = "latest") -> DatasetSchemaResponse:
        try:
            parquet_path = self.storage.resolve_dataset_local_path(dataset_id, version)
        except Exception as e:
            raise DatasetNotFoundError(f"Dataset '{dataset_id}' not found: {e}")

        arrow_schema = self.engine.get_schema(str(parquet_path))
        columns = [
            DatasetColumnSchema(
                name=field.name,
                type=str(field.type),
                nullable=field.nullable
            ) for field in arrow_schema
        ]
        return DatasetSchemaResponse(
            dataset_id=dataset_id,
            version=version,
            columns=columns,
            total_columns=len(columns)
        )

    def get_versions(self, dataset_id: str) -> DatasetVersionsResponse:
        # Check that dataset exists
        self.get_schema(dataset_id)
        
        # 1. Attempt gRPC query to Catalog Service
        catalog_detail = self.catalog_grpc.get_dataset(dataset_id)
        if catalog_detail and catalog_detail.versions:
            versions = [
                DatasetVersionItem(
                    version=f"v{v.version_number}",
                    commit_hash=v.checksum or v.version_id,
                    created_at=v.created_at or datetime.now(timezone.utc).isoformat(),
                    is_latest=(idx == len(catalog_detail.versions) - 1)
                ) for idx, v in enumerate(catalog_detail.versions)
            ]
            return DatasetVersionsResponse(
                dataset_id=dataset_id,
                versions=versions,
                total_versions=len(versions)
            )

        # 2. Default fallback
        versions = [
            DatasetVersionItem(
                version="v1",
                commit_hash="sha256_initial_standardized_version",
                created_at=datetime.now(timezone.utc).isoformat(),
                is_latest=True
            )
        ]
        return DatasetVersionsResponse(
            dataset_id=dataset_id,
            versions=versions,
            total_versions=len(versions)
        )

    def get_status(self, dataset_id: str) -> DatasetStatusResponse:
        try:
            parquet_path = self.storage.resolve_dataset_local_path(dataset_id)
            is_ready = parquet_path.exists()
            status = DatasetStatus.SERVING if is_ready else DatasetStatus.PREPROCESSED
        except Exception:
            status = DatasetStatus.ARCHIVED
            is_ready = False

        return DatasetStatusResponse(
            dataset_id=dataset_id,
            status=status,
            version="latest",
            is_ready_for_serving=is_ready,
            updated_at=datetime.now(timezone.utc).isoformat()
        )

    def execute_query(self, spec: QuerySpecification) -> Tuple[pa.Table, int]:
        try:
            parquet_path = self.storage.resolve_dataset_local_path(spec.dataset_id, spec.version)
        except Exception as e:
            raise DatasetNotFoundError(f"Dataset '{spec.dataset_id}' not found: {e}")

        table = self.engine.execute_query(str(parquet_path), spec)
        total_matching_rows = self.engine.execute_count(str(parquet_path), spec)
        return table, total_matching_rows

    def export_dataset(self, dataset_id: str, version: str, format_code: str) -> Tuple[Iterator[bytes], str, str]:
        spec = QuerySpecification(dataset_id=dataset_id, version=version, page=1, page_size=1000000)
        table, _ = self.execute_query(spec)
        strategy = ExportStrategyFactory.get_strategy(format_code)
        stream_iter = strategy.stream(table)
        filename = f"dataset_{dataset_id}_{version}.{strategy.file_extension}"
        return stream_iter, strategy.content_type, filename
