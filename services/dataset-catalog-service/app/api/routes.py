from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.dataset_metadata import DatasetMetadata
from app.models.storage_reference import StorageReference
from app.models.processing_status import ProcessingStatus
from app.schemas.dataset import (
    DatasetCreate,
    DatasetResponse,
    DatasetDetailResponse,
    IdentityResolveRequest,
    IdentityResolveResponse,
    DuplicateCheckRequest,
    DuplicateCheckResponse
)
from app.schemas.dataset_version import (
    VersionResponse,
    VersionDetailResponse,
    VersionStatusResponse,
    ProcessingStatusItem,
    StorageReferenceResponse
)
from app.schemas.dataset_metadata import MetadataResponse
from app.schemas.event import PreprocessingResultMessage
from app.schemas.common import APIResponse, PaginatedResponse, PaginatedData
from app.services.dataset_registration_service import dataset_registration_manager
from app.services.identity_resolution_service import identity_resolution_manager
from app.services.duplicate_detection_service import duplicate_detector
from app.services.preprocessing_consumer import preprocessing_result_consumer
from app.logger import logger

router = APIRouter(prefix="/api/v1/catalog", tags=["Dataset Catalog"])


@router.post("/datasets", response_model=APIResponse[DatasetDetailResponse], status_code=status.HTTP_201_CREATED)
async def register_dataset(
    payload: DatasetCreate,
    force_re_registration: bool = Query(default=False),
    db: AsyncSession = Depends(get_db)
):
    """Registers a new dataset or dataset version."""
    try:
        dataset, version = await dataset_registration_manager.register_dataset(
            db, payload.model_dump(), force_re_registration=force_re_registration
        )

        # Query full details
        query = (
            select(Dataset)
            .options(selectinload(Dataset.versions))
            .where(Dataset.dataset_id == dataset.dataset_id)
        )
        res = await db.execute(query)
        full_dataset = res.scalar_one()

        return APIResponse(
            success=True,
            message="Dataset registered successfully",
            data=DatasetDetailResponse.model_validate(full_dataset)
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error registering dataset: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/datasets", response_model=PaginatedResponse[DatasetResponse])
async def list_datasets(
    name: Optional[str] = None,
    domain: Optional[str] = None,
    source: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Lists, filters, and searches datasets with pagination."""
    query = select(Dataset)
    count_query = select(func.count(Dataset.dataset_id))

    if name:
        query = query.where(Dataset.name.ilike(f"%{name}%"))
        count_query = count_query.where(Dataset.name.ilike(f"%{name}%"))
    if domain:
        query = query.where(Dataset.domain == domain)
        count_query = count_query.where(Dataset.domain == domain)
    if source:
        query = query.where(Dataset.source == source)
        count_query = count_query.where(Dataset.source == source)

    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    offset = (page - 1) * limit
    query = query.order_by(Dataset.created_at.desc()).offset(offset).limit(limit)

    res = await db.execute(query)
    datasets = res.scalars().all()
    total_pages = ceil(total / limit) if limit > 0 else 1

    items = [DatasetResponse.model_validate(d) for d in datasets]

    return PaginatedResponse(
        success=True,
        message="Datasets retrieved successfully",
        data=PaginatedData(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    )


@router.get("/datasets/{dataset_id}", response_model=APIResponse[DatasetDetailResponse])
async def get_dataset_detail(
    dataset_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves dataset details and version history."""
    query = (
        select(Dataset)
        .options(selectinload(Dataset.versions))
        .where(Dataset.dataset_id == dataset_id)
    )
    res = await db.execute(query)
    dataset = res.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    return APIResponse(
        success=True,
        message="Dataset retrieved successfully",
        data=DatasetDetailResponse.model_validate(dataset)
    )


@router.get(
    "/datasets/{dataset_id}/versions/{version_id}",
    response_model=APIResponse[VersionDetailResponse]
)
async def get_version_detail(
    dataset_id: str,
    version_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves specific version details, metadata entries, and storage reference."""
    query = (
        select(DatasetVersion)
        .options(
            selectinload(DatasetVersion.metadata_entries),
            selectinload(DatasetVersion.storage_reference)
        )
        .where(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.version_id == version_id
        )
    )
    res = await db.execute(query)
    version = res.scalar_one_or_none()

    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset version not found")

    return APIResponse(
        success=True,
        message="Version detail retrieved successfully",
        data=VersionDetailResponse.model_validate(version)
    )


@router.get(
    "/datasets/{dataset_id}/versions/{version_id}/status",
    response_model=APIResponse[VersionStatusResponse]
)
async def get_version_status(
    dataset_id: str,
    version_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves version processing status and state transition history."""
    query = (
        select(DatasetVersion)
        .options(selectinload(DatasetVersion.processing_statuses))
        .where(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.version_id == version_id
        )
    )
    res = await db.execute(query)
    version = res.scalar_one_or_none()

    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset version not found")

    history = [
        ProcessingStatusItem.model_validate(ps)
        for ps in sorted(version.processing_statuses, key=lambda x: x.processed_at)
    ]

    return APIResponse(
        success=True,
        message="Version status retrieved successfully",
        data=VersionStatusResponse(
            version_id=version.version_id,
            current_status=version.status,
            history=history
        )
    )


@router.post("/resolve-identity", response_model=APIResponse[IdentityResolveResponse])
async def resolve_identity(
    payload: IdentityResolveRequest,
    db: AsyncSession = Depends(get_db)
):
    """Resolves whether a dataset is new or matches an existing dataset entity."""
    is_existing, dataset, matched_by = await identity_resolution_manager.resolve_identity(
        db, payload.model_dump()
    )

    return APIResponse(
        success=True,
        message="Identity resolution executed",
        data=IdentityResolveResponse(
            is_existing=is_existing,
            dataset_id=dataset.dataset_id if dataset else None,
            matched_by=matched_by
        )
    )


@router.post("/check-duplicate", response_model=APIResponse[DuplicateCheckResponse])
async def check_duplicate(
    payload: DuplicateCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """Checks whether a dataset version with matching checksum/storage_ref already exists."""
    is_duplicate, dataset_id, version_id = await duplicate_detector.check_duplicate(
        db, payload.model_dump()
    )

    return APIResponse(
        success=True,
        message="Duplicate check executed",
        data=DuplicateCheckResponse(
            is_duplicate=is_duplicate,
            existing_dataset_id=dataset_id,
            existing_version_id=version_id,
            matched_checksum=payload.checksum
        )
    )


@router.post("/preprocessing-result", response_model=APIResponse[dict])
async def receive_preprocessing_result(
    payload: PreprocessingResultMessage,
    db: AsyncSession = Depends(get_db)
):
    """Callback endpoint to receive dataset preprocessing result events."""
    success = await preprocessing_result_consumer.handle_processing_result(
        db, payload.model_dump()
    )
    await db.commit()

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process preprocessing result payload"
        )

    return APIResponse(
        success=True,
        message="Preprocessing result received and processed",
        data={"version_id": payload.version_id, "status": payload.status}
    )
