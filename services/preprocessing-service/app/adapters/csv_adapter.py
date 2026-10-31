"""
CSV / TSV Dataset Adapter.
Supports streaming delimiter-separated values with encoding fallbacks (UTF-8, Latin-1).
"""
from pathlib import Path
from typing import Iterator, Dict, Optional
import pandas as pd
from app.adapters.base import IDatasetAdapter
from app.core.exceptions import ParsingError
from app.config.logger import get_logger

logger = get_logger(__name__)


class CSVAdapter(IDatasetAdapter):
    """Adapter for delimited text datasets (CSV, TSV, semicolon-separated)."""

    def __init__(self, file_path: Path, delimiter: Optional[str] = None):
        super().__init__(file_path)
        self.delimiter = delimiter or self._infer_delimiter()

    def _infer_delimiter(self) -> str:
        """Infers the delimiter from the first few lines."""
        if self.file_path.suffix.lower() == ".tsv":
            return "\t"
        try:
            with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                first_line = f.readline()
                if "\t" in first_line and "," not in first_line:
                    return "\t"
                if ";" in first_line and "," not in first_line:
                    return ";"
        except Exception:
            pass
        return ","

    def stream_records(self, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        try:
            for chunk in pd.read_csv(
                self.file_path,
                sep=self.delimiter,
                chunksize=chunk_size,
                encoding="utf-8",
                on_bad_lines="skip"
            ):
                yield chunk
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 decode failed for {self.file_path.name}, falling back to latin1")
            for chunk in pd.read_csv(
                self.file_path,
                sep=self.delimiter,
                chunksize=chunk_size,
                encoding="latin1",
                on_bad_lines="skip"
            ):
                yield chunk
        except Exception as e:
            raise ParsingError(f"Failed to stream CSV data from {self.file_path.name}: {e}")

    def read_all(self, max_rows: Optional[int] = None) -> pd.DataFrame:
        try:
            try:
                return pd.read_csv(
                    self.file_path,
                    sep=self.delimiter,
                    nrows=max_rows,
                    encoding="utf-8",
                    on_bad_lines="skip"
                )
            except UnicodeDecodeError:
                return pd.read_csv(
                    self.file_path,
                    sep=self.delimiter,
                    nrows=max_rows,
                    encoding="latin1",
                    on_bad_lines="skip"
                )
        except Exception as e:
            raise ParsingError(f"Failed to read CSV dataset: {e}")

    def get_schema(self) -> Dict[str, str]:
        sample = self.read_all(max_rows=100)
        return {col: str(dtype) for col, dtype in sample.dtypes.items()}

    def get_record_count(self) -> int:
        with open(self.file_path, "rb") as f:
            lines = sum(1 for _ in f)
        return max(0, lines - 1)  # Subtract header line
