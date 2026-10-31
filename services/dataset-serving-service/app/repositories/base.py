"""
Dataset Repository Interface (Repository Pattern).
Defines contracts for data access, schema inspection, version tracking, and querying.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Iterator, Optional
import pyarrow as pa
from app.schemas.dataset import (
    DatasetMetadataResponse,
    DatasetSchemaResponse,
    DatasetVersionsResponse,
    DatasetSearchResultItem,
    DatasetStatusResponse
)
from app.builders.query_builder import QuerySpecification


class IDatasetRepository(ABC):
    """Abstract Repository for querying datasets and inspecting metadata."""

    @abstractmethod
    def search_datasets(self, query: Optional[str] = None, format_code: Optional[str] = None) -> List[DatasetSearchResultItem]:
        """Searches indexed datasets matching keywords or formats."""
        pass

    @abstractmethod
    def get_metadata(self, dataset_id: str, version: str = "latest") -> DatasetMetadataResponse:
        """Retrieves statistical metadata and profile for the given dataset version."""
        pass

    @abstractmethod
    def get_schema(self, dataset_id: str, version: str = "latest") -> DatasetSchemaResponse:
        """Extracts column schemas, data types, and nullability."""
        pass

    @abstractmethod
    def get_versions(self, dataset_id: str) -> DatasetVersionsResponse:
        """Lists historical versions and commit hashes for the dataset."""
        pass

    @abstractmethod
    def get_status(self, dataset_id: str) -> DatasetStatusResponse:
        """Retrieves dataset lifecycle and serving readiness status."""
        pass

    @abstractmethod
    def execute_query(self, spec: QuerySpecification) -> Tuple[pa.Table, int]:
        """Executes analytical query specification, returning (table_slice, total_matching_rows)."""
        pass

    @abstractmethod
    def export_dataset(self, dataset_id: str, version: str, format_code: str) -> Tuple[Iterator[bytes], str, str]:
        """Streams dataset export, returning (bytes_stream, content_type, filename)."""
        pass
