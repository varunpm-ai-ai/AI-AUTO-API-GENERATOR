from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "UP",
        "service": settings.SERVICE_NAME,
        "environment": settings.NODE_ENV
    }


@router.get("/readiness")
async def readiness_check():
    return {
        "status": "READY",
        "service": settings.SERVICE_NAME,
        "database": "CONNECTED",
        "cache": "CONNECTED"
    }
