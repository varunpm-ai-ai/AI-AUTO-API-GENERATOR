"""
Cached Dataset Repository Proxy (Proxy / Decorator Pattern).
Transparently caches query results, schema responses, and dataset metadata.
"""
from typing import List, Tuple, Iterator, Optional, Any, Dict
import pyarrow as pa
from app.repositories.base import IDatasetRepository
from app.schemas.dataset import (
    DatasetMetadataResponse,
    DatasetSchemaResponse,
    DatasetVersionsResponse,
    DatasetSearchResultItem,
    DatasetStatusResponse
)
from app.builders.query_builder import QuerySpecification
from app.cache.manager import cache_manager
from app.config.logger import get_logger

logger = get_logger(__name__)


class CachedDatasetRepository(IDatasetRepository):
    """Proxy decorator for IDatasetRepository adding multi-tier caching."""

    def __init__(self, inner_repo: IDatasetRepository):
        self.inner = inner_repo
        self.cache = cache_manager

    def search_datasets(self, query: Optional[str] = None, format_code: Optional[str] = None) -> List[DatasetSearchResultItem]:
        cache_key = f"search:{query or 'all'}:{format_code or 'all'}"
        cached = self.cache.get(cache_key)
        if cached:
            return [DatasetSearchResultItem.model_validate(item) for item in cached]

        results = self.inner.search_datasets(query, format_code)
        self.cache.set(cache_key, [r.model_dump() for r in results], ttl=60)
        return results

    def get_metadata(self, dataset_id: str, version: str = "latest") -> DatasetMetadataResponse:
        cache_key = f"meta:{dataset_id}:{version}"
        cached = self.cache.get(cache_key)
        if cached:
            return DatasetMetadataResponse.model_validate(cached)

        meta = self.inner.get_metadata(dataset_id, version)
        self.cache.set(cache_key, meta.model_dump(), ttl=self.cache.meta_ttl)
        return meta

    def get_schema(self, dataset_id: str, version: str = "latest") -> DatasetSchemaResponse:
        cache_key = f"schema:{dataset_id}:{version}"
        cached = self.cache.get(cache_key)
        if cached:
            return DatasetSchemaResponse.model_validate(cached)

        schema = self.inner.get_schema(dataset_id, version)
        self.cache.set(cache_key, schema.model_dump(), ttl=self.cache.meta_ttl)
        return schema

    def get_versions(self, dataset_id: str) -> DatasetVersionsResponse:
        cache_key = f"versions:{dataset_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return DatasetVersionsResponse.model_validate(cached)

        versions = self.inner.get_versions(dataset_id)
        self.cache.set(cache_key, versions.model_dump(), ttl=self.cache.meta_ttl)
        return versions

    def get_status(self, dataset_id: str) -> DatasetStatusResponse:
        return self.inner.get_status(dataset_id)

    def execute_query(self, spec: QuerySpecification) -> Tuple[pa.Table, int]:
        """
        Executes query with query cache lookup.
        Returns Arrow Table and total matching rows.
        """
        cache_key = f"query:{spec.dataset_id}:{spec.get_cache_key()}"
        cached = self.cache.get(cache_key)

        if cached:
            logger.info(f"Query cache HIT for dataset {spec.dataset_id}")
            records = cached.get("records", [])
            total_rows = cached.get("total_rows", len(records))
            table = pa.Table.from_pylist(records) if records else pa.Table.from_batches([])
            return table, total_rows

        logger.debug(f"Query cache MISS for dataset {spec.dataset_id}")
        table, total_rows = self.inner.execute_query(spec)

        # Cache serialized records and total count
        df = table.to_pandas()
        self.cache.set(
            cache_key,
            {"records": df.to_dict(orient="records"), "total_rows": total_rows},
            ttl=self.cache.query_ttl
        )
        return table, total_rows

    def export_dataset(self, dataset_id: str, version: str, format_code: str) -> Tuple[Iterator[bytes], str, str]:
        # Direct pass-through for streaming export downloads
        return self.inner.export_dataset(dataset_id, version, format_code)
