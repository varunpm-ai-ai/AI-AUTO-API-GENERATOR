"""
Parquet Streaming Export Strategy.
"""
from typing import Iterator
import io
import pyarrow as pa
import pyarrow.parquet as pq
from app.strategies.base import IExportFormatStrategy


class ParquetExportStrategy(IExportFormatStrategy):
    """Streams binary compressed Apache Parquet."""

    @property
    def content_type(self) -> str:
        return "application/x-parquet"

    @property
    def file_extension(self) -> str:
        return "parquet"

    def stream(self, table: pa.Table, chunk_size: int = 1000) -> Iterator[bytes]:
        sink = io.BytesIO()
        pq.write_table(table, sink, compression="snappy")
        sink.seek(0)
        while True:
            chunk = sink.read(64 * 1024)
            if not chunk:
                break
            yield chunk
