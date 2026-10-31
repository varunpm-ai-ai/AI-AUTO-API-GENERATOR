from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Centralized configuration management for the Dataset Serving Service.
    Loads values from environment variables with optional .env file support.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Core Service Settings
    PORT: int = Field(default=5005, description="HTTP Port for the Dataset Serving Service")
    HOST: str = Field(default="0.0.0.0", description="Bind Host")
    ENVIRONMENT: str = Field(default="development", description="Runtime Environment")
    SERVICE_NAME: str = Field(default="dataset-serving-service", description="Microservice Name")
    LOG_LEVEL: str = Field(default="INFO", description="Log Level")

    # Caching & Redis Configuration (L2 Cache & Rate Limiting)
    REDIS_URL: str = Field(default="redis://localhost:6379/1", description="Redis Connection URL")
    QUERY_CACHE_TTL_SECONDS: int = Field(default=300, description="Query cache TTL in seconds")
    METADATA_CACHE_TTL_SECONDS: int = Field(default=1800, description="Metadata cache TTL in seconds")
    ENABLE_CACHE: bool = Field(default=True, description="Enable or disable query caching")

    # Object Storage (MinIO / S3)
    S3_ENDPOINT: str = Field(default="localhost:9000", description="MinIO/S3 Host Endpoint")
    S3_ACCESS_KEY: str = Field(default="minioadmin", description="S3 Access Key")
    S3_SECRET_KEY: str = Field(default="minioadmin", description="S3 Secret Key")
    S3_BUCKET_PROCESSED: str = Field(default="processed-data", description="Bucket holding standardized Parquet datasets")
    S3_USE_SSL: bool = Field(default=False, description="Whether to use SSL for S3 connection")

    # Upstream Integrations
    CATALOG_SERVICE_URL: str = Field(default="http://localhost:5003", description="Dataset Catalog Service URL")
    CATALOG_GRPC_HOST: str = Field(default="localhost", description="Dataset Catalog gRPC Host")
    CATALOG_GRPC_PORT: int = Field(default=50053, description="Dataset Catalog gRPC Port")

    # Rate Limiting & Query Protection
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=120, description="Max allowed requests per minute per IP/User")
    RATE_LIMIT_BURST: int = Field(default=30, description="Max burst allowance")

    # Analytical Engine (DuckDB & PyArrow) Limits
    MAX_SCAN_ROWS_LIMIT: int = Field(default=500000, description="Maximum row scan quota per query")
    MAX_PAGE_SIZE: int = Field(default=1000, description="Maximum allowed rows per page")
    DEFAULT_PAGE_SIZE: int = Field(default=50, description="Default rows per page")
    QUERY_TIMEOUT_SECONDS: int = Field(default=15, description="Timeout in seconds for query execution")
    DUCKDB_MAX_MEMORY_MB: int = Field(default=1536, description="Memory limit for DuckDB query engine")
    DUCKDB_THREADS: int = Field(default=4, description="Threads for DuckDB parallel processing")
    ENABLE_SQL_SANDBOX: bool = Field(default=True, description="Enforce strict read-only AST safety validation")

    # Authentication & Security
    JWT_SECRET: str = Field(default="super-secret-key-change-in-production", description="JWT Secret Key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT Algorithm")
    REQUIRE_AUTH: bool = Field(default=False, description="Enforce mandatory JWT authentication check")


settings = Settings()
