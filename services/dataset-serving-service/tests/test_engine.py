"""
Unit Tests for Analytical Query Engine (DuckDB Vectorized Scan).
"""
from pathlib import Path
from app.engines.duckdb_engine import DuckDBAnalyticalEngine
from app.builders.query_builder import QuerySpecification, QuerySpecificationBuilder
from app.schemas.query import FilterOperator, SortDirection


def test_duckdb_schema_and_count(setup_test_dataset):
    engine = DuckDBAnalyticalEngine()
    parquet_path = f"./tmp/serving_cache/{setup_test_dataset}/latest/dataset_{setup_test_dataset}.parquet"

    schema = engine.get_schema(parquet_path)
    assert "id" in schema.names
    assert "name" in schema.names
    assert "salary" in schema.names

    count = engine.get_row_count(parquet_path)
    assert count == 5


def test_duckdb_projection_and_filtering(setup_test_dataset):
    engine = DuckDBAnalyticalEngine()
    parquet_path = f"./tmp/serving_cache/{setup_test_dataset}/latest/dataset_{setup_test_dataset}.parquet"

    # Query: SELECT id, name WHERE age > 30 ORDER BY id DESC LIMIT 2
    spec = (
        QuerySpecificationBuilder(dataset_id=setup_test_dataset)
        .select(["id", "name"])
        .where("age", FilterOperator.GT, 30)
        .sort_by("id", SortDirection.DESC)
        .paginate(page=1, page_size=2)
        .build()
    )

    result_table = engine.execute_query(parquet_path, spec)
    assert len(result_table) == 2
    assert result_table.column_names == ["id", "name"]
    
    df = result_table.to_pandas()
    # Age > 30 has ids 3, 4, 5. DESC order gives 5, 4
    assert list(df["id"]) == [5, 4]

    # Total matching count
    total_matching = engine.execute_count(parquet_path, spec)
    assert total_matching == 3
