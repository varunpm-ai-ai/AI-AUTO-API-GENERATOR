"""
JSON & JSON-Lines (NDJSON) Dataset Adapter.
Supports streaming large nested or flat JSON payloads.
"""
from pathlib import Path
from typing import Iterator, Dict, Optional
import pandas as pd
import json
from app.adapters.base import IDatasetAdapter
from app.core.exceptions import ParsingError
from app.config.logger import get_logger

logger = get_logger(__name__)


class JSONAdapter(IDatasetAdapter):
    """Adapter for JSON Array and JSON Lines (ndjson) formats."""

    def __init__(self, file_path: Path, is_lines: Optional[bool] = None):
        super().__init__(file_path)
        self.is_lines = is_lines if is_lines is not None else self._check_is_lines()

    def _check_is_lines(self) -> bool:
        if self.file_path.suffix.lower() in [".jsonl", ".ndjson"]:
            return True
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                first_char = f.read(1).strip()
                return first_char != "["
        except Exception:
            return False

    def stream_records(self, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        try:
            if self.is_lines:
                for chunk in pd.read_json(
                    self.file_path,
                    lines=True,
                    chunksize=chunk_size,
                    encoding="utf-8"
                ):
                    yield chunk
            else:
                # If full JSON array, load and chunk in memory
                df = self.read_all()
                total_len = len(df)
                for i in range(0, total_len, chunk_size):
                    yield df.iloc[i:i + chunk_size]
        except Exception as e:
            raise ParsingError(f"Failed to stream JSON data from {self.file_path.name}: {e}")

    def read_all(self, max_rows: Optional[int] = None) -> pd.DataFrame:
        try:
            if self.is_lines:
                return pd.read_json(self.file_path, lines=True, nrows=max_rows, encoding="utf-8")
            
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                # Search for root collection key if dictionary wrapper
                for val in data.values():
                    if isinstance(val, list):
                        data = val
                        break
                else:
                    data = [data]

            df = pd.json_normalize(data)
            if max_rows:
                df = df.head(max_rows)
            return df
        except Exception as e:
            raise ParsingError(f"Failed to read JSON dataset: {e}")

    def get_schema(self) -> Dict[str, str]:
        sample = self.read_all(max_rows=100)
        return {col: str(dtype) for col, dtype in sample.dtypes.items()}

    def get_record_count(self) -> int:
        if self.is_lines:
            with open(self.file_path, "rb") as f:
                return sum(1 for _ in f)
        df = self.read_all()
        return len(df)
