from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.dataset_version import VersionResponse, VersionDetailResponse


class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    domain: str = Field(..., min_length=1, max_length=100)
    source: str = Field(..., min_length=1, max_length=255)
    checksum: str = Field(..., min_length=1, max_length=64)
    storage_ref: str = Field(..., min_length=1, max_length=512)
    storage_type: str = Field(default="object_storage", max_length=50)
    file_size: int = Field(default=0, ge=0)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dataset_id: str
    name: str
    description: Optional[str] = None
    domain: str
    source: str
    created_at: datetime
    updated_at: datetime



class DatasetDetailResponse(DatasetResponse):
    versions: List[VersionResponse] = []


class DatasetFilterParams(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    source: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)


class IdentityResolveRequest(BaseModel):
    name: str
    source: str
    domain: str


class IdentityResolveResponse(BaseModel):
    is_existing: bool
    dataset_id: Optional[str] = None
    matched_by: str  # e.g., "exact_match", "source_name_match", "none"


class DuplicateCheckRequest(BaseModel):
    checksum: str
    storage_ref: Optional[str] = None


class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    existing_dataset_id: Optional[str] = None
    existing_version_id: Optional[str] = None
    matched_checksum: str
