"""
Pydantic Models and Schemas for Preprocessing Job Contracts.
"""
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, UUID4, ConfigDict
import uuid


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ImputationMethod(str, Enum):
    MEAN = "MEAN"
    MEDIAN = "MEDIAN"
    MODE = "MODE"
    CONSTANT = "CONSTANT"
    DROP = "DROP"


class CleaningStrategyOptions(BaseModel):
    """Configurable options for data cleaning strategies."""
    model_config = ConfigDict(extra="ignore")

    deduplicate: bool = Field(default=True, description="Remove duplicate rows")
    dedup_subset_columns: Optional[List[str]] = Field(default=None, description="Subset of columns for deduplication")
    
    sanitize_strings: bool = Field(default=True, description="Trim leading/trailing whitespaces and unprintable characters")
    normalize_column_names: bool = Field(default=True, description="Convert column names to lower_snake_case")
    
    null_imputation: ImputationMethod = Field(default=ImputationMethod.DROP, description="Strategy for missing values")
    imputation_constant_value: Any = Field(default=None, description="Constant value if imputation method is CONSTANT")
    
    handle_outliers: bool = Field(default=False, description="Detect and clamp numerical outliers")
    outlier_threshold_iqr: float = Field(default=1.5, description="IQR multiplier for outlier fences")


class JobRequestPayload(BaseModel):
    """Inbound job contract received via RabbitMQ or REST trigger."""
    model_config = ConfigDict(extra="ignore")

    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique Preprocessing Job Identifier")
    dataset_id: str = Field(..., description="Target Dataset Identifier in Catalog")
    source_uri: str = Field(..., description="S3 or local URI pointing to acquired raw dataset file")
    format_hint: Optional[str] = Field(default=None, description="Optional format hint (e.g. csv, json, xlsx)")
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Trace correlation ID")
    cleaning_options: CleaningStrategyOptions = Field(default_factory=CleaningStrategyOptions)


class JobResultResponse(BaseModel):
    """Output contract reported to Kafka and Catalog service upon completion."""
    model_config = ConfigDict(extra="ignore")

    job_id: str
    dataset_id: str
    status: JobStatus
    processed_uri: Optional[str] = None
    row_count: int = 0
    column_count: int = 0
    detected_format: Optional[str] = None
    schema_definition: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    validation_report: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0
    error_message: Optional[str] = None
