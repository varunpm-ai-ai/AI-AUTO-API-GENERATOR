"""
Dataset Serving Service Entry Point.
Initializes FastAPI, mounts HTTP routes, registers exception handlers, and configures lifespan.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config.settings import settings
from app.config.logger import get_logger
from app.core.exceptions import ServingBaseException

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(f"Starting {settings.SERVICE_NAME} on port {settings.PORT} [{settings.ENVIRONMENT}]")
    yield
    logger.info(f"Shutting down {settings.SERVICE_NAME}...")


app = FastAPI(
    title="Dataset Serving Service",
    description="Microservice for analytical querying, schema inspection, projection, and streaming exports.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ServingBaseException)
async def serving_exception_handler(request: Request, exc: ServingBaseException):
    """Centralized exception normalizer for all domain exceptions."""
    logger.warning(f"Operational error on {request.method} {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details
        }
    )


# Mount Routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=(settings.ENVIRONMENT == "development"))
