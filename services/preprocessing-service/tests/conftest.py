import pytest
import tempfile
import json
from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


@pytest.fixture
def temp_dir():
    """Provides an ephemeral directory for creating test fixture files."""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def sample_csv_path(temp_dir):
    """Generates a sample CSV file with headers, whitespace, and nulls."""
    csv_file = temp_dir / "sample.csv"
    data = (
        "id, name , age ,salary\n"
        "1, Alice , 28 , 85000\n"
        "2, Bob   ,    , 92000\n"
        "3, Charlie, 35 , \n"
        "1, Alice , 28 , 85000\n"  # Duplicate
    )
    csv_file.write_text(data, encoding="utf-8")
    return csv_file


@pytest.fixture
def sample_json_path(temp_dir):
    """Generates a sample JSON file."""
    json_file = temp_dir / "sample.json"
    data = [
        {"id": 101, "product": "Widget A", "price": 19.99},
        {"id": 102, "product": "Widget B", "price": 29.50},
        {"id": 103, "product": "Widget C", "price": 4.95}
    ]
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return json_file


@pytest.fixture
def sample_parquet_path(temp_dir):
    """Generates a sample Apache Parquet file."""
    parquet_file = temp_dir / "sample.parquet"
    df = pd.DataFrame({
        "item_id": [1, 2, 3],
        "quantity": [10, 20, 30],
        "in_stock": [True, True, False]
    })
    table = pa.Table.from_pandas(df)
    pq.write_table(table, str(parquet_file))
    return parquet_file
