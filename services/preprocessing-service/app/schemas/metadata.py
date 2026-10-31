"""
Metadata & Profiling Schemas for Preprocessing Output.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ColumnStatistic(BaseModel):
    """Statistical summary for an individual column."""
    name: str
    inferred_type: str
    total_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean: Optional[float] = None
    sample_values: List[Any] = Field(default_factory=list)


class DatasetProfile(BaseModel):
    """Aggregate profile of the processed dataset."""
    row_count: int
    column_count: int
    columns: List[ColumnStatistic]
    memory_usage_bytes: int
    file_size_bytes: int
    checksum_sha256: str
