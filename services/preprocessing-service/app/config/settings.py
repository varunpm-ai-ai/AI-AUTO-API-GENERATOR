from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """
    Centralized configuration management for the Preprocessing Service.
    Loads values from environment variables with optional .env file support.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Core Service Settings
    PORT: int = Field(default=5004, description="HTTP Port for the Preprocessing Service")
    HOST: str = Field(default="0.0.0.0", description="Bind host")
    ENVIRONMENT: str = Field(default="development", description="Runtime environment")
    SERVICE_NAME: str = Field(default="preprocessing-service", description="Microservice Name")
    LOG_LEVEL: str = Field(default="INFO", description="Log level")

    # RabbitMQ AMQP Configuration
    RABBITMQ_URL: str = Field(default="amqp://guest:guest@localhost:5672/", description="RabbitMQ Connection URL")
    RABBITMQ_QUEUE: str = Field(default="dataset.preprocess.jobs", description="Inbound Job Queue")
    RABBITMQ_DLQ: str = Field(default="dataset.preprocess.dlq", description="Dead Letter Queue")
    RABBITMQ_PREFETCH_COUNT: int = Field(default=2, description="Channel Prefetch Limit")
    RABBITMQ_MAX_RETRIES: int = Field(default=3, description="Maximum Retry Attempts before DLQ")

    # Kafka Event Streaming Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092", description="Kafka Bootstrap Servers")
    KAFKA_TOPIC_PREPROCESSED: str = Field(default="dataset.preprocessed", description="Kafka Topic for Success Events")
    KAFKA_TOPIC_FAILED: str = Field(default="dataset.preprocess.failed", description="Kafka Topic for Failure Events")

    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis Connection URL")
    IDEMPOTENCY_TTL_SECONDS: int = Field(default=3600, description="Idempotency Key TTL in seconds")

    # S3 / MinIO Object Storage
    S3_ENDPOINT: str = Field(default="localhost:9000", description="S3/MinIO Host Endpoint")
    S3_ACCESS_KEY: str = Field(default="minioadmin", description="S3 Access Key")
    S3_SECRET_KEY: str = Field(default="minioadmin", description="S3 Secret Key")
    S3_BUCKET_RAW: str = Field(default="raw-datasets", description="Bucket holding raw datasets")
    S3_BUCKET_PROCESSED: str = Field(default="processed-data", description="Bucket holding processed Parquet files")
    S3_USE_SSL: bool = Field(default=False, description="Whether to use SSL with S3")

    # Upstream Integrations
    CATALOG_SERVICE_URL: str = Field(default="http://localhost:5003", description="Dataset Catalog Service URL")

    # Guardrails & NFR Limits
    MAX_MEMORY_MB: int = Field(default=2048, description="Maximum Memory Limit in MB")
    PROCESSING_TIMEOUT_SECONDS: int = Field(default=300, description="Max Processing Duration per Job")
    MAX_CHUNK_SIZE_ROWS: int = Field(default=10000, description="Row chunk size for streaming")
    MAX_FILE_SIZE_BYTES: int = Field(default=524288000, description="500MB maximum raw file size")
    MAX_DECOMPRESSED_RATIO: int = Field(default=10, description="Zip-bomb protection ratio limit")
    TEMP_SCRATCH_DIR: str = Field(default="./tmp/scratch", description="Base scratch directory")


settings = Settings()
