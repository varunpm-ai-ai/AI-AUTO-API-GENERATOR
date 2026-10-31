"""
Apache Parquet Dataset Adapter.
High-performance columnar adapter utilizing PyArrow RecordBatches for streaming.
"""
from pathlib import Path
from typing import Iterator, Dict, Optional
import pandas as pd
import pyarrow.parquet as pq
from app.adapters.base import IDatasetAdapter
from app.core.exceptions import ParsingError


class ParquetAdapter(IDatasetAdapter):
    """Adapter for Apache Parquet columnar datasets."""

    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self._parquet_file = pq.ParquetFile(str(file_path))

    def stream_records(self, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        try:
            for batch in self._parquet_file.iter_batches(batch_size=chunk_size):
                yield batch.to_pandas()
        except Exception as e:
            raise ParsingError(f"Failed to stream Parquet batches from {self.file_path.name}: {e}")

    def read_all(self, max_rows: Optional[int] = None) -> pd.DataFrame:
        try:
            table = self._parquet_file.read()
            df = table.to_pandas()
            if max_rows:
                df = df.head(max_rows)
            return df
        except Exception as e:
            raise ParsingError(f"Failed to read Parquet dataset: {e}")

    def get_schema(self) -> Dict[str, str]:
        schema = self._parquet_file.schema_arrow
        return {field.name: str(field.type) for field in schema}

    def get_record_count(self) -> int:
        return self._parquet_file.metadata.num_rows
