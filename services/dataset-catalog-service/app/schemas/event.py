from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DatasetAcquiredEventPayload(BaseModel):
    event_id: str
    dataset_name: str
    source: str
    domain: str
    storage_ref: str
    checksum: str
    file_size: int = 0
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    acquired_at: Optional[str] = None


class PreprocessingJobMessage(BaseModel):
    job_id: str
    dataset_id: str
    version_id: str
    storage_ref: str
    checksum: str
    published_at: str


class PreprocessingResultMessage(BaseModel):
    job_id: str
    dataset_id: str
    version_id: str
    status: str  # "COMPLETED" or "FAILED"
    error_message: Optional[str] = None
    extracted_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    completed_at: str
