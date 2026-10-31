"""
PDF Dataset Adapter.
Extracts tabular text lines from PDF documents into structured tabular data.
"""
from pathlib import Path
from typing import Iterator, Dict, Optional, List
import pandas as pd
from pypdf import PdfReader
from app.adapters.base import IDatasetAdapter
from app.core.exceptions import ParsingError
from app.config.logger import get_logger

logger = get_logger(__name__)


class PDFAdapter(IDatasetAdapter):
    """Adapter for extracting structured textual or tabular lines from PDF datasets."""

    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self._reader = PdfReader(str(file_path))

    def _extract_rows(self) -> List[Dict[str, str]]:
        rows = []
        for page_idx, page in enumerate(self._reader.pages):
            text = page.extract_text()
            if not text:
                continue
            for line_idx, line in enumerate(text.splitlines()):
                line_content = line.strip()
                if line_content:
                    rows.append({
                        "page_number": page_idx + 1,
                        "line_number": line_idx + 1,
                        "text_content": line_content
                    })
        return rows

    def stream_records(self, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        df = self.read_all()
        for i in range(0, len(df), chunk_size):
            yield df.iloc[i:i + chunk_size]

    def read_all(self, max_rows: Optional[int] = None) -> pd.DataFrame:
        try:
            rows = self._extract_rows()
            df = pd.DataFrame(rows)
            if df.empty:
                df = pd.DataFrame(columns=["page_number", "line_number", "text_content"])
            if max_rows:
                df = df.head(max_rows)
            return df
        except Exception as e:
            raise ParsingError(f"Failed to extract structured data from PDF {self.file_path.name}: {e}")

    def get_schema(self) -> Dict[str, str]:
        return {
            "page_number": "int64",
            "line_number": "int64",
            "text_content": "string"
        }

    def get_record_count(self) -> int:
        return len(self.read_all())
