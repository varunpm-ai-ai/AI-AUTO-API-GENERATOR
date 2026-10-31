"""
FastAPI HTTP Routes for Preprocessing Service.
Provides Health, Readiness, and Direct REST Preprocessing Triggers.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from datetime import datetime, timezone
import asyncio
from app.schemas.job import JobRequestPayload, JobResultResponse
from app.commands.preprocess_command import PreprocessingJobCommand
from app.config.settings import settings
from app.messaging.rabbitmq_consumer import rabbitmq_consumer
from app.config.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Basic liveness probe."""
    return {
        "status": "UP",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """Readiness probe checking subsystem operational states."""
    return {
        "status": "READY",
        "service": settings.SERVICE_NAME,
        "rabbitmq_connected": rabbitmq_consumer.is_running,
        "storage_endpoint": settings.S3_ENDPOINT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/api/v1/preprocess", response_model=JobResultResponse, status_code=status.HTTP_200_OK)
async def preprocess_dataset(payload: JobRequestPayload) -> JobResultResponse:
    """
    Direct synchronous / REST execution of the preprocessing pipeline.
    Invoked for ad-hoc processing, gateway forwarding, or integration tests.
    """
    logger.info(f"Received manual REST preprocessing request for dataset {payload.dataset_id}")
    command = PreprocessingJobCommand(payload)
    
    # Run in executor to prevent event loop blocking
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, command.execute)

    if result.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=result.model_dump()
        )
    return result
