"""
NDJSON / JSONL Streaming Export Strategy.
"""
from typing import Iterator
import json
import pyarrow as pa
from app.strategies.base import IExportFormatStrategy


class NDJSONExportStrategy(IExportFormatStrategy):
    """Streams data as newline-delimited JSON objects (JSON Lines)."""

    @property
    def content_type(self) -> str:
        return "application/x-ndjson; charset=utf-8"

    @property
    def file_extension(self) -> str:
        return "jsonl"

    def stream(self, table: pa.Table, chunk_size: int = 1000) -> Iterator[bytes]:
        df = table.to_pandas()
        for row in df.to_dict(orient="records"):
            line = json.dumps(row) + "\n"
            yield line.encode("utf-8")
