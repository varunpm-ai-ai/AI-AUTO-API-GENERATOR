import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SERVICE_NAME: str = "dataset-catalog-service"
    PORT: int = 5003
    GRPC_PORT: int = 50053
    NODE_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "sqlite+aiosqlite:///./catalog.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    TOPIC_DATASET_ACQUIRED: str = "dataset.acquired"
    TOPIC_DATASET_REGISTERED: str = "dataset.registered"
    TOPIC_DATASET_PROCESSING_STARTED: str = "dataset.processing.started"
    TOPIC_DATASET_PROCESSING_COMPLETED: str = "dataset.processing.completed"
    TOPIC_DATASET_PROCESSING_FAILED: str = "dataset.processing.failed"
    TOPIC_DATASET_READY: str = "dataset.ready"

    QUEUE_PREPROCESSING_JOBS: str = "dataset.preprocessing"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
