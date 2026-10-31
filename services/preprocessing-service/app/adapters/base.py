"""
Base Dataset Adapter Interface (Adapter Pattern).
Defines the standard contract for reading, streaming, and profiling heterogeneous dataset formats.
"""
from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any, Optional
from pathlib import Path
import pandas as pd


class IDatasetAdapter(ABC):
    """
    Target interface that normalizes disparate file formats (CSV, JSON, Parquet, Excel, PDF)
    into a uniform tabular streaming and inspection contract.
    """
    def __init__(self, file_path: Path):
        self.file_path = file_path

    @abstractmethod
    def stream_records(self, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        """Yields chunks of records as pandas DataFrames to prevent high memory usage."""
        pass

    @abstractmethod
    def read_all(self, max_rows: Optional[int] = None) -> pd.DataFrame:
        """Reads the full dataset or up to max_rows into memory."""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, str]:
        """Returns inferred column names and their data types."""
        pass

    @abstractmethod
    def get_record_count(self) -> int:
        """Returns the total number of records/rows in the dataset."""
        pass
