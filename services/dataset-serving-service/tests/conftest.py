import pytest
from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


@pytest.fixture(scope="session", autouse=True)
def setup_test_dataset():
    """Generates a test parquet dataset in local serving cache so all tests can query it."""
    dataset_id = "test-dataset-001"
    version = "latest"
    cache_dir = Path("./tmp/serving_cache") / dataset_id / version
    cache_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = cache_dir / f"dataset_{dataset_id}.parquet"

    df = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "age": [25, 30, 35, 40, 45],
        "salary": [70000.0, 80000.0, 90000.0, 100000.0, 110000.0],
        "department": ["Engineering", "Product", "Engineering", "Design", "Product"]
    })
    table = pa.Table.from_pandas(df)
    pq.write_table(table, str(parquet_path), compression="snappy")

    yield dataset_id
