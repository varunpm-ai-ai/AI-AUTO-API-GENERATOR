from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.dataset_metadata import MetadataResponse


class StorageReferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    storage_id: str
    version_id: str
    uri: str
    storage_type: str
    file_size: int
    checksum: str
    created_at: datetime


class VersionCreate(BaseModel):
    checksum: str = Field(..., min_length=1, max_length=64)
    storage_ref: str = Field(..., min_length=1, max_length=512)
    storage_type: str = Field(default="object_storage", max_length=50)
    file_size: int = Field(default=0, ge=0)
    metadata: Optional[dict] = Field(default_factory=dict)


class VersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version_id: str
    dataset_id: str
    version_number: int
    checksum: str
    storage_ref: str
    status: str
    created_at: datetime


class VersionDetailResponse(VersionResponse):
    metadata_entries: List[MetadataResponse] = []
    storage_reference: Optional[StorageReferenceResponse] = None


class ProcessingStatusItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status_id: str
    state: str
    error_message: Optional[str] = None
    processed_at: datetime


class VersionStatusResponse(BaseModel):
    version_id: str
    current_status: str
    history: List[ProcessingStatusItem] = []

