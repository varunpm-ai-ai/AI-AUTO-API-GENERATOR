from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class MetadataCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    value: Any
    source: str = Field(default="system", max_length=100)


class MetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metadata_id: str
    version_id: str
    key: str
    value: str
    source: str
    created_at: datetime

