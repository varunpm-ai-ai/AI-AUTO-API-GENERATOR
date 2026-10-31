"""
Unit Tests for Export Format Strategies (Strategy Pattern).
"""
import pyarrow as pa
from app.strategies.csv_strategy import CSVExportStrategy
from app.strategies.json_strategy import JSONExportStrategy
from app.strategies.ndjson_strategy import NDJSONExportStrategy
from app.strategies.parquet_strategy import ParquetExportStrategy
from app.strategies.factory import ExportStrategyFactory


def test_export_strategies():
    table = pa.Table.from_pydict({
        "id": [1, 2],
        "name": ["Alice", "Bob"]
    })

    # Test CSV
    csv_strat = ExportStrategyFactory.get_strategy("csv")
    csv_bytes = b"".join(csv_strat.stream(table))
    assert b"Alice" in csv_bytes
    assert b"Bob" in csv_bytes

    # Test JSON
    json_strat = ExportStrategyFactory.get_strategy("json")
    json_bytes = b"".join(json_strat.stream(table))
    assert b'"id": 1' in json_bytes
    assert json_bytes.startswith(b"[\n")

    # Test NDJSON
    ndjson_strat = ExportStrategyFactory.get_strategy("jsonl")
    ndjson_bytes = b"".join(ndjson_strat.stream(table))
    lines = [line for line in ndjson_bytes.split(b"\n") if line]
    assert len(lines) == 2

    # Test Parquet
    parquet_strat = ExportStrategyFactory.get_strategy("parquet")
    pq_bytes = b"".join(parquet_strat.stream(table))
    assert pq_bytes.startswith(b"PAR1")
