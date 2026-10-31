"""
Export Format Strategy Interface (Strategy Pattern).
Defines contracts for streaming datasets in heterogeneous formats (JSON, CSV, NDJSON, Parquet).
"""
from abc import ABC, abstractmethod
from typing import Iterator
import pyarrow as pa


class IExportFormatStrategy(ABC):
    """Abstract Strategy for serializing PyArrow Tables into HTTP streaming bytes."""

    @property
    @abstractmethod
    def content_type(self) -> str:
        """HTTP Content-Type response header."""
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension for downloaded artifact."""
        pass

    @abstractmethod
    def stream(self, table: pa.Table, chunk_size: int = 1000) -> Iterator[bytes]:
        """Yields chunks of serialized bytes for streaming responses."""
        pass
