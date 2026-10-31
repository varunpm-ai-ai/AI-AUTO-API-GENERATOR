"""
Export Strategy Factory.
Resolves format strategies based on format string or MIME type.
"""
from app.strategies.base import IExportFormatStrategy
from app.strategies.csv_strategy import CSVExportStrategy
from app.strategies.json_strategy import JSONExportStrategy
from app.strategies.ndjson_strategy import NDJSONExportStrategy
from app.strategies.parquet_strategy import ParquetExportStrategy
from app.core.exceptions import QueryValidationError


class ExportStrategyFactory:
    """Factory selecting the IExportFormatStrategy for file downloads."""

    _STRATEGIES = {
        "csv": CSVExportStrategy(),
        "text/csv": CSVExportStrategy(),
        "json": JSONExportStrategy(),
        "application/json": JSONExportStrategy(),
        "jsonl": NDJSONExportStrategy(),
        "ndjson": NDJSONExportStrategy(),
        "application/x-ndjson": NDJSONExportStrategy(),
        "parquet": ParquetExportStrategy(),
        "application/x-parquet": ParquetExportStrategy()
    }

    @classmethod
    def get_strategy(cls, format_code: str = "csv") -> IExportFormatStrategy:
        strategy = cls._STRATEGIES.get(format_code.lower())
        if not strategy:
            raise QueryValidationError(f"Unsupported export format: '{format_code}'. Supported: csv, json, jsonl, parquet")
        return strategy
