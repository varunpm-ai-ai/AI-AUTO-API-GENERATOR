"""
Uniform API Response Formatting and Pagination Envelopes.
"""
from typing import TypeVar, Generic, Optional, List, Dict, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMetadata(BaseModel):
    page: int
    page_size: int
    total_rows: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next_cursor: Optional[str] = None


class APIResponse(BaseModel, Generic[T]):
    """Standardized API response envelope for all serving endpoints."""
    status: str = "success"
    data: T
    meta: Dict[str, Any] = Field(default_factory=dict)
    pagination: Optional[PaginationMetadata] = None
    duration_ms: float = 0.0
    cached: bool = False
