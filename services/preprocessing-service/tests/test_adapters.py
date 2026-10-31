"""
Unit Tests for IDatasetAdapter Implementations (Adapter Pattern).
"""
import pytest
from app.adapters.csv_adapter import CSVAdapter
from app.adapters.json_adapter import JSONAdapter
from app.adapters.parquet_adapter import ParquetAdapter
from app.factories.adapter_factory import DatasetAdapterFactory


def test_csv_adapter_streaming_and_schema(sample_csv_path):
    adapter = CSVAdapter(sample_csv_path)
    
    # Test read_all
    df = adapter.read_all()
    assert len(df) == 4
    assert "id" in df.columns

    # Test streaming chunks
    chunks = list(adapter.stream_records(chunk_size=2))
    assert len(chunks) == 2
    assert sum(len(c) for c in chunks) == 4

    # Test schema inference
    schema = adapter.get_schema()
    assert "id" in schema


def test_json_adapter_reading(sample_json_path):
    adapter = JSONAdapter(sample_json_path)
    df = adapter.read_all()
    assert len(df) == 3
    assert "product" in df.columns
    assert adapter.get_record_count() == 3


def test_parquet_adapter_streaming(sample_parquet_path):
    adapter = ParquetAdapter(sample_parquet_path)
    df = adapter.read_all()
    assert len(df) == 3
    assert "quantity" in df.columns
    assert adapter.get_record_count() == 3

    # Test batch streaming
    batches = list(adapter.stream_records(chunk_size=1))
    assert len(batches) == 3


def test_adapter_factory_resolution(sample_csv_path, sample_json_path, sample_parquet_path):
    csv_ad = DatasetAdapterFactory.get_adapter(sample_csv_path, "csv")
    assert isinstance(csv_ad, CSVAdapter)

    json_ad = DatasetAdapterFactory.get_adapter(sample_json_path, "json")
    assert isinstance(json_ad, JSONAdapter)

    pq_ad = DatasetAdapterFactory.get_adapter(sample_parquet_path, "parquet")
    assert isinstance(pq_ad, ParquetAdapter)
