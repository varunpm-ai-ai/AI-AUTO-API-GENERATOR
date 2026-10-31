"""
Analytical Query Engine Interface (Analytical Abstraction).
Defines contracts for columnar querying, schema inspection, and row counting.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path
import pyarrow as pa
from app.builders.query_builder import QuerySpecification


class IAnalyticalEngine(ABC):
    """Abstract analytical scanning engine over Parquet datasets."""

    @abstractmethod
    def execute_query(self, parquet_path: str, spec: QuerySpecification) -> pa.Table:
        """Executes projection, filtering, sorting, and pagination, returning an Arrow Table."""
        pass

    @abstractmethod
    def execute_count(self, parquet_path: str, spec: QuerySpecification) -> int:
        """Returns the total filtered row count matching the specification."""
        pass

    @abstractmethod
    def get_schema(self, parquet_path: str) -> pa.Schema:
        """Extracts the PyArrow Schema without scanning data rows."""
        pass

    @abstractmethod
    def get_row_count(self, parquet_path: str) -> int:
        """Returns total unconstrained rows in the dataset."""
        pass
