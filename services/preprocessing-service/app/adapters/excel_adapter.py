"""
Excel (XLSX / XLS) Dataset Adapter.
Supports reading multi-sheet workbooks using openpyxl.
"""
from pathlib import Path
from typing import Iterator, Dict, Optional
import pandas as pd
from app.adapters.base import IDatasetAdapter
from app.core.exceptions import ParsingError


class ExcelAdapter(IDatasetAdapter):
    """Adapter for Excel spreadsheets."""

    def __init__(self, file_path: Path, sheet_name: Optional[str] = None):
        super().__init__(file_path)
        self.sheet_name = sheet_name or 0

    def stream_records(self, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        df = self.read_all()
        for i in range(0, len(df), chunk_size):
            yield df.iloc[i:i + chunk_size]

    def read_all(self, max_rows: Optional[int] = None) -> pd.DataFrame:
        try:
            return pd.read_excel(
                self.file_path,
                sheet_name=self.sheet_name,
                nrows=max_rows,
                engine="openpyxl"
            )
        except Exception as e:
            raise ParsingError(f"Failed to read Excel dataset from {self.file_path.name}: {e}")

    def get_schema(self) -> Dict[str, str]:
        sample = self.read_all(max_rows=100)
        return {col: str(dtype) for col, dtype in sample.dtypes.items()}

    def get_record_count(self) -> int:
        df = self.read_all()
        return len(df)
