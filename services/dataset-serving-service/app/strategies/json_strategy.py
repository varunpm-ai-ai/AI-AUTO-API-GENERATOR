"""
JSON Streaming Export Strategy.
"""
from typing import Iterator
import json
import pyarrow as pa
from app.strategies.base import IExportFormatStrategy


class JSONExportStrategy(IExportFormatStrategy):
    """Streams dataset records as a standard JSON array."""

    @property
    def content_type(self) -> str:
        return "application/json; charset=utf-8"

    @property
    def file_extension(self) -> str:
        return "json"

    def stream(self, table: pa.Table, chunk_size: int = 1000) -> Iterator[bytes]:
        yield b"[\n"
        df = table.to_pandas()
        total_rows = len(df)
        for i, row in enumerate(df.to_dict(orient="records")):
            line = json.dumps(row)
            if i < total_rows - 1:
                line += ",\n"
            else:
                line += "\n"
            yield line.encode("utf-8")
        yield b"]"
