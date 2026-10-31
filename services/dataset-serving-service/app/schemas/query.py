"""
Analytical Query Contracts, Filter Specifications, and Pagination Schemas.
"""
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class FilterOperator(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    CONTAINS = "contains"
    LIKE = "like"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class FilterCondition(BaseModel):
    model_config = ConfigDict(extra="ignore")
    column: str
    operator: FilterOperator = FilterOperator.EQ
    value: Optional[Union[str, int, float, bool, List[Any]]] = None


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortClause(BaseModel):
    column: str
    direction: SortDirection = SortDirection.ASC


class QueryRequest(BaseModel):
    """Structured query request contract for filtering, projection, and pagination."""
    model_config = ConfigDict(extra="ignore")

    columns: Optional[List[str]] = Field(default=None, description="Projection: subset of columns to retrieve")
    filters: Optional[List[FilterCondition]] = Field(default=None, description="List of filter conditions (ANDed together)")
    sort: Optional[List[SortClause]] = Field(default=None, description="Sorting criteria")
    page: int = Field(default=1, ge=1, description="Page index (1-based)")
    page_size: int = Field(default=50, ge=1, le=1000, description="Number of records per page")
    cursor: Optional[str] = Field(default=None, description="Opaque cursor token for cursor-based pagination")
    raw_sql: Optional[str] = Field(default=None, description="Optional sanitized SQL where clause or subquery")
    version: Optional[str] = Field(default="latest", description="Dataset version tag or commit hash")
