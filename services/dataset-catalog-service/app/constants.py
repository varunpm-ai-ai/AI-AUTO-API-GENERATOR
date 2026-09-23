from enum import Enum


class LifecycleState(str, Enum):
    RAW_REGISTERED = "RAW_REGISTERED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class RegistrationType(str, Enum):
    NEW = "NEW"
    EXISTING = "EXISTING"
    RE_REGISTRATION = "RE_REGISTRATION"


class OutboxStatus(str, Enum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class EventStatus(str, Enum):
    RECEIVED = "RECEIVED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Topics:
    DATASET_ACQUIRED = "dataset.acquired"
    DATASET_REGISTERED = "dataset.registered"
    DATASET_PROCESSING_STARTED = "dataset.processing.started"
    DATASET_PROCESSING_COMPLETED = "dataset.processing.completed"
    DATASET_PROCESSING_FAILED = "dataset.processing.failed"
    DATASET_READY = "dataset.ready"


class Queues:
    PREPROCESSING_JOBS = "dataset.preprocessing"
