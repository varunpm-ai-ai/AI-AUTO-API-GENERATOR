"""
Preprocessing Service Entry Point.
Initializes FastAPI application, mounts HTTP routes, and orchestrates asynchronous background consumers.
"""
from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config.settings import settings
from app.config.logger import get_logger
from app.messaging.rabbitmq_consumer import rabbitmq_consumer
from app.messaging.kafka_producer import kafka_publisher

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan Manager.
    Manages startup and shutdown routines for message brokers and workers.
    """
    logger.info(f"Starting {settings.SERVICE_NAME} on port {settings.PORT} [{settings.ENVIRONMENT}]")

    # Start RabbitMQ consumer task
    consumer_task = asyncio.create_task(rabbitmq_consumer.start())

    yield

    logger.info(f"Shutting down {settings.SERVICE_NAME}...")
    await rabbitmq_consumer.stop()
    await kafka_publisher.stop()
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    logger.info("Service shutdown complete.")


app = FastAPI(
    title="Preprocessing Service",
    description="Microservice for dataset extraction, parsing, normalization, cleaning, validation, and Parquet persistence.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=(settings.ENVIRONMENT == "development"))
