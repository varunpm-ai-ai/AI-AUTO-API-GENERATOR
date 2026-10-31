"""
Dataset Adapter & Extractor Factory (Factory Pattern).
Instantiates the appropriate IDatasetAdapter or Extractor based on MIME or format identifier.
"""
from pathlib import Path
from typing import Type
from app.adapters.base import IDatasetAdapter
from app.adapters.csv_adapter import CSVAdapter
from app.adapters.json_adapter import JSONAdapter
from app.adapters.parquet_adapter import ParquetAdapter
from app.adapters.excel_adapter import ExcelAdapter
from app.adapters.pdf_adapter import PDFAdapter
from app.core.exceptions import ParsingError
from app.config.logger import get_logger

logger = get_logger(__name__)


class DatasetAdapterFactory:
    """Factory creating concrete IDatasetAdapter instances."""

    _ADAPTER_MAP = {
        "csv": CSVAdapter,
        "tsv": CSVAdapter,
        "text/csv": CSVAdapter,
        "json": JSONAdapter,
        "jsonl": JSONAdapter,
        "ndjson": JSONAdapter,
        "application/json": JSONAdapter,
        "application/x-ndjson": JSONAdapter,
        "parquet": ParquetAdapter,
        "application/x-parquet": ParquetAdapter,
        "xlsx": ExcelAdapter,
        "xls": ExcelAdapter,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ExcelAdapter,
        "pdf": PDFAdapter,
        "application/pdf": PDFAdapter
    }

    @classmethod
    def get_adapter(cls, file_path: Path, format_code: str) -> IDatasetAdapter:
        """
        Resolves and instantiates the matching IDatasetAdapter for the detected file.
        """
        fmt_key = format_code.lower()
        adapter_cls = cls._ADAPTER_MAP.get(fmt_key)

        if not adapter_cls:
            # Fallback by file extension
            ext = file_path.suffix.lower().lstrip(".")
            adapter_cls = cls._ADAPTER_MAP.get(ext)

        if not adapter_cls:
            raise ParsingError(f"No dataset adapter registered for format: '{format_code}' (file: {file_path.name})")

        logger.debug(f"Resolved adapter {adapter_cls.__name__} for format '{format_code}'")
        return adapter_cls(file_path)
