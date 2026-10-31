"""
Dataset Metadata, Schema, Version, and Search Schemas.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DatasetStatus(str, Enum):
    ACQUIRED = "ACQUIRED"
    PREPROCESSED = "PREPROCESSED"
    SERVING = "SERVING"
    READY = "READY"
    ARCHIVED = "ARCHIVED"


class DatasetColumnSchema(BaseModel):
    name: str
    type: str
    nullable: bool = True
    description: Optional[str] = None


class DatasetSchemaResponse(BaseModel):
    dataset_id: str
    version: str
    columns: List[DatasetColumnSchema]
    total_columns: int


class ColumnProfileStat(BaseModel):
    name: str
    inferred_type: str
    null_count: int = 0
    null_percentage: float = 0.0
    unique_count: int = 0
    min: Optional[Any] = None
    max: Optional[Any] = None
    mean: Optional[float] = None
    sample_values: List[str] = Field(default_factory=list)


class DatasetMetadataResponse(BaseModel):
    dataset_id: str
    version: str
    status: DatasetStatus
    row_count: int
    column_count: int
    memory_usage_bytes: int = 0
    checksum_sha256: Optional[str] = None
    storage_uri: Optional[str] = None
    columns: List[ColumnProfileStat] = Field(default_factory=list)
    created_at: Optional[str] = None


class DatasetVersionItem(BaseModel):
    version: str
    commit_hash: str
    created_at: str
    is_latest: bool = False
    row_count: int = 0


class DatasetVersionsResponse(BaseModel):
    dataset_id: str
    versions: List[DatasetVersionItem]
    total_versions: int


class DatasetSearchResultItem(BaseModel):
    dataset_id: str
    name: str
    description: Optional[str] = None
    status: DatasetStatus
    version: str
    format: str = "parquet"
    row_count: int = 0
    tags: List[str] = Field(default_factory=list)


class DatasetStatusResponse(BaseModel):
    dataset_id: str
    status: DatasetStatus
    version: str
    is_ready_for_serving: bool
    updated_at: str
