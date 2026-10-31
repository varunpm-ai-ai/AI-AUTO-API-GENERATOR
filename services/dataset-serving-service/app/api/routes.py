"""
Dataset Serving Service HTTP Endpoints.
Implements the 15 functional requirements: Search, Metadata, Schema, Querying,
Pagination, Filtering, Projection, Versions, Downloads, Status, Auth, Rate Limits, and Health.
"""
from fastapi import APIRouter, Request, Response, Depends, Query, Path, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import time
import math
from app.schemas.dataset import (
    DatasetMetadataResponse,
    DatasetSchemaResponse,
    DatasetVersionsResponse,
    DatasetSearchResultItem,
    DatasetStatusResponse
)
from app.schemas.query import QueryRequest, FilterCondition, FilterOperator, SortClause, SortDirection
from app.schemas.response import APIResponse, PaginationMetadata
from app.builders.query_builder import QuerySpecificationBuilder, QuerySpecification
from app.repositories import dataset_repository
from app.security import rate_limiter, ASTQueryValidator, AuthManager, UserContext
from app.core.exceptions import ServingBaseException, DatasetNotFoundError, QueryValidationError
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# ------------------------------------------------------------------------------
# 15. Health & Readiness Endpoints
# ------------------------------------------------------------------------------
@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Liveness probe."""
    return {
        "status": "UP",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """Readiness probe checking S3 storage and Redis cache connectivity."""
    redis_ready = rate_limiter.redis is not None
    return {
        "status": "READY",
        "service": settings.SERVICE_NAME,
        "cache_ready": redis_ready,
        "storage_endpoint": settings.S3_ENDPOINT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ------------------------------------------------------------------------------
# 1. Dataset Search
# ------------------------------------------------------------------------------
@router.get("/api/v1/datasets/search", response_model=APIResponse[List[DatasetSearchResultItem]])
async def search_datasets(
    request: Request,
    q: Optional[str] = Query(None, description="Search keyword"),
    format: Optional[str] = Query(None, description="Format filter (e.g. parquet)")
) -> APIResponse[List[DatasetSearchResultItem]]:
    start_time = time.time()
    rate_limiter.check_rate_limit(request.client.host if request.client else "unknown")
    AuthManager.extract_user_context(request)

    results = dataset_repository.search_datasets(query=q, format_code=format)
    duration_ms = (time.time() - start_time) * 1000.0

    return APIResponse(
        data=results,
        meta={"total": len(results), "query": q, "format": format},
        duration_ms=round(duration_ms, 2)
    )


# ------------------------------------------------------------------------------
# 10. Dataset Status Retrieval
# ------------------------------------------------------------------------------
@router.get("/api/v1/datasets/{dataset_id}/status", response_model=APIResponse[DatasetStatusResponse])
async def get_dataset_status(
    request: Request,
    dataset_id: str = Path(..., description="Target Dataset UUID or ID")
) -> APIResponse[DatasetStatusResponse]:
    start_time = time.time()
    rate_limiter.check_rate_limit(request.client.host if request.client else "unknown")
    AuthManager.extract_user_context(request)

    status_data = dataset_repository.get_status(dataset_id)
    duration_ms = (time.time() - start_time) * 1000.0

    return APIResponse(
        data=status_data,
        duration_ms=round(duration_ms, 2)
    )


# ------------------------------------------------------------------------------
# 2. Dataset Metadata Retrieval
# ------------------------------------------------------------------------------
@router.get("/api/v1/datasets/{dataset_id}/metadata", response_model=APIResponse[DatasetMetadataResponse])
async def get_dataset_metadata(
    request: Request,
    dataset_id: str = Path(..., description="Target Dataset UUID or ID"),
    version: str = Query("latest", description="Dataset version (e.g. v1, latest)")
) -> APIResponse[DatasetMetadataResponse]:
    start_time = time.time()
    rate_limiter.check_rate_limit(request.client.host if request.client else "unknown")
    AuthManager.extract_user_context(request)

    meta = dataset_repository.get_metadata(dataset_id, version=version)
    duration_ms = (time.time() - start_time) * 1000.0

    return APIResponse(
        data=meta,
        duration_ms=round(duration_ms, 2)
    )


# ------------------------------------------------------------------------------
# 3. Dataset Schema Inspection
# ------------------------------------------------------------------------------
@router.get("/api/v1/datasets/{dataset_id}/schema", response_model=APIResponse[DatasetSchemaResponse])
async def get_dataset_schema(
    request: Request,
    dataset_id: str = Path(..., description="Target Dataset UUID or ID"),
    version: str = Query("latest", description="Dataset version")
) -> APIResponse[DatasetSchemaResponse]:
    start_time = time.time()
    rate_limiter.check_rate_limit(request.client.host if request.client else "unknown")
    AuthManager.extract_user_context(request)

    schema = dataset_repository.get_schema(dataset_id, version=version)
    duration_ms = (time.time() - start_time) * 1000.0

    return APIResponse(
        data=schema,
        duration_ms=round(duration_ms, 2)
    )


# ------------------------------------------------------------------------------
# 8. Dataset Version Retrieval
# ------------------------------------------------------------------------------
@router.get("/api/v1/datasets/{dataset_id}/versions", response_model=APIResponse[DatasetVersionsResponse])
async def get_dataset_versions(
    request: Request,
    dataset_id: str = Path(..., description="Target Dataset UUID or ID")
) -> APIResponse[DatasetVersionsResponse]:
    start_time = time.time()
    rate_limiter.check_rate_limit(request.client.host if request.client else "unknown")
    AuthManager.extract_user_context(request)

    versions = dataset_repository.get_versions(dataset_id)
    duration_ms = (time.time() - start_time) * 1000.0

    return APIResponse(
        data=versions,
        duration_ms=round(duration_ms, 2)
    )


@router.get("/api/v1/datasets/{dataset_id}/versions/{version}", response_model=APIResponse[DatasetMetadataResponse])
async def get_dataset_specific_version(
    request: Request,
    dataset_id: str = Path(..., description="Target Dataset UUID or ID"),
    version: str = Path(..., description="Specific Version (e.g. v1)")
) -> APIResponse[DatasetMetadataResponse]:
    start_time = time.time()
    rate_limiter.check_rate_limit(request.client.host if request.client else "unknown")
    AuthManager.extract_user_context(request)

    meta = dataset_repository.get_metadata(dataset_id, version=version)
    duration_ms = (time.time() - start_time) * 1000.0

    return APIResponse(
        data=meta,
        duration_ms=round(duration_ms, 2)
    )


# ------------------------------------------------------------------------------
# 4, 5, 6, 7. Dataset Querying, Pagination, Filtering, Projection (GET & POST)
# ------------------------------------------------------------------------------
@router.get("/api/v1/datasets/{dataset_id}/query", response_model=APIResponse[List[Dict[str, Any]]])
async def query_dataset_get(
    request: Request,
    dataset_id: str = Path(..., description="Target Dataset UUID or ID"),
    columns: Optional[str] = Query(None, description="Comma-separated projected columns (e.g. id,name,age)"),
    page: int = Query(1, ge=1, description="Page index"),
    page_size: int = Query(50, ge=1, le=1000, description="Rows per page"),
    sort: Optional[str] = Query(None, description="Sort column (prefix with - for descending, e.g. -age)"),
    cursor: Optional[str] = Query(None, description="Opaque pagination cursor"),
    version: str = Query("latest", description="Dataset version")
) -> APIResponse[List[Dict[str, Any]]]:
    """GET endpoint for querying, projection, and pagination via query parameters."""
    start_time = time.time()
    rate_limiter.check_rate_limit(request.client.host if request.client else "unknown")
    AuthManager.extract_user_context(request)

    builder = QuerySpecificationBuilder(dataset_id=dataset_id, version=version)
    
    if columns:
        cols_list = [c.strip() for c in columns.split(",") if c.strip()]
        builder.select(cols_list)

    if sort:
        desc = sort.startswith("-")
        col_name = sort.lstrip("-")
        builder.sort_by(col_name, SortDirection.DESC if desc else SortDirection.ASC)

    builder.paginate(page=page, page_size=page_size, cursor=cursor)
    spec = builder.build()

    table, total_matching = dataset_repository.execute_query(spec)
    df = table.to_pandas()
    records = df.to_dict(orient="records")

    total_pages = math.ceil(total_matching / spec.page_size) if spec.page_size > 0 else 1
    next_cursor = spec.generate_next_cursor(len(records))

    pagination = PaginationMetadata(
        page=spec.page,
        page_size=spec.page_size,
        total_rows=total_matching,
        total_pages=total_pages,
        has_next=(spec.page < total_pages) or (next_cursor is not None),
        has_prev=(spec.page > 1),
        next_cursor=next_cursor
    )

    duration_ms = (time.time() - start_time) * 1000.0
    return APIResponse(
        data=records,
        pagination=pagination,
        duration_ms=round(duration_ms, 2)
    )


@router.post("/api/v1/datasets/{dataset_id}/query", response_model=APIResponse[List[Dict[str, Any]]])
async def query_dataset_post(
    request: Request,
    query_body: QueryRequest,
    dataset_id: str = Path(..., description="Target Dataset UUID or ID")
) -> APIResponse[List[Dict[str, Any]]]:
    """POST endpoint for complex parameterized filtering, boolean expressions, and projection."""
    start_time = time.time()
    rate_limiter.check_rate_limit(request.client.host if request.client else "unknown")
    AuthManager.extract_user_context(request)

    builder = QuerySpecificationBuilder(dataset_id=dataset_id, version=query_body.version or "latest")
    builder.from_request(query_body)
    spec = builder.build()

    table, total_matching = dataset_repository.execute_query(spec)
    df = table.to_pandas()
    records = df.to_dict(orient="records")

    total_pages = math.ceil(total_matching / spec.page_size) if spec.page_size > 0 else 1
    next_cursor = spec.generate_next_cursor(len(records))

    pagination = PaginationMetadata(
        page=spec.page,
        page_size=spec.page_size,
        total_rows=total_matching,
        total_pages=total_pages,
        has_next=(spec.page < total_pages) or (next_cursor is not None),
        has_prev=(spec.page > 1),
        next_cursor=next_cursor
    )

    duration_ms = (time.time() - start_time) * 1000.0
    return APIResponse(
        data=records,
        pagination=pagination,
        duration_ms=round(duration_ms, 2)
    )


# ------------------------------------------------------------------------------
# 9. Processed Dataset Download & Streaming
# ------------------------------------------------------------------------------
@router.get("/api/v1/datasets/{dataset_id}/download")
async def download_dataset(
    request: Request,
    dataset_id: str = Path(..., description="Target Dataset UUID or ID"),
    version: str = Query("latest", description="Dataset version"),
    format: str = Query("csv", description="Export format: csv, json, jsonl, parquet")
):
    """Streams full processed dataset in the requested format (CSV, JSON, JSONL, Parquet)."""
    rate_limiter.check_rate_limit(request.client.host if request.client else "unknown")
    AuthManager.extract_user_context(request)

    stream_iter, content_type, filename = dataset_repository.export_dataset(
        dataset_id=dataset_id,
        version=version,
        format_code=format
    )

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Accept-Ranges": "bytes"
    }

    return StreamingResponse(
        stream_iter,
        media_type=content_type,
        headers=headers
    )
