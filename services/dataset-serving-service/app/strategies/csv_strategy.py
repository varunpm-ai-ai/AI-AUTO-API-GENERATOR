"""
CSV Streaming Export Strategy.
"""
from typing import Iterator
import io
import pyarrow as pa
import pyarrow.csv as pacsv
from app.strategies.base import IExportFormatStrategy


class CSVExportStrategy(IExportFormatStrategy):
    """Streams data as comma-separated values."""

    @property
    def content_type(self) -> str:
        return "text/csv; charset=utf-8"

    @property
    def file_extension(self) -> str:
        return "csv"

    def stream(self, table: pa.Table, chunk_size: int = 1000) -> Iterator[bytes]:
        sink = io.BytesIO()
        pacsv.write_csv(table, sink)
        sink.seek(0)
        while True:
            chunk = sink.read(64 * 1024)
            if not chunk:
                break
            yield chunk
