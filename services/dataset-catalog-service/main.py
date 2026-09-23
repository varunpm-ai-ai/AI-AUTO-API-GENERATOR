import asyncio
import sys
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.redis_client import redis_client
from app.api.health import router as health_router
from app.api.routes import router as catalog_router
from app.services.event_publisher_service import event_publisher
from app.services.kafka_consumer_service import kafka_consumer_service
from app.services.preprocessing_publisher import preprocessing_job_publisher
from app.grpc_server.server import start_grpc_server
from app.logger import logger

# Context manager for FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Dataset Catalog Service...")

    # Initialize Database tables
    await init_db()

    # Connect to Redis
    await redis_client.connect()

    # Connect RabbitMQ publisher
    await preprocessing_job_publisher.connect()

    # Start background event publisher (outbox polling)
    publisher_task = asyncio.create_task(event_publisher.start_worker())

    # Start background Kafka consumer
    kafka_task = asyncio.create_task(kafka_consumer_service.start_listening())

    # Start gRPC Server
    grpc_server = await start_grpc_server()

    logger.info(f"Dataset Catalog Service is running on HTTP port {settings.PORT} and gRPC port {settings.GRPC_PORT}.")

    yield

    logger.info("Shutting down Dataset Catalog Service...")

    # Cancel background tasks
    publisher_task.cancel()
    kafka_task.cancel()

    await event_publisher.stop()
    await kafka_consumer_service.stop()
    await preprocessing_job_publisher.close()
    await redis_client.close()

    if grpc_server:
        await grpc_server.stop(grace=3)

    logger.info("Dataset Catalog Service shutdown complete.")


app = FastAPI(
    title="Dataset Catalog Service",
    description="Microservice responsible for dataset identity resolution, duplicate detection, versioning, metadata & lifecycle management.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(catalog_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=False)
