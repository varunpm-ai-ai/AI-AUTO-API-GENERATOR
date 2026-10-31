"""
Domain Exceptions for the Preprocessing Service.
Provides typed, granular operational exceptions with status codes and contextual details.
"""
from typing import Optional, Any, Dict


class PreprocessingBaseException(Exception):
    """Base exception for all Preprocessing Service errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.status_code = status_code


class JobValidationError(PreprocessingBaseException):
    """Raised when an incoming job payload fails schema or contract validation."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=400)


class FileDetectionError(PreprocessingBaseException):
    """Raised when file type cannot be determined or is unsupported."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=422)


class ExtractionSecurityError(PreprocessingBaseException):
    """Raised when archive violates security boundaries (zip bomb, path traversal)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=403)


class ParsingError(PreprocessingBaseException):
    """Raised when dataset content cannot be parsed by the selected adapter."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=422)


class NormalizationError(PreprocessingBaseException):
    """Raised during schema or type normalization failures."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=422)


class DataCleaningError(PreprocessingBaseException):
    """Raised when a cleaning strategy execution encounters an unrecoverable state."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=422)


class DatasetValidationError(PreprocessingBaseException):
    """Raised when processed data fails data-quality invariants."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=422)


class StorageError(PreprocessingBaseException):
    """Raised when reading from or writing to object storage fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=502)


class ProcessingTimeoutError(PreprocessingBaseException):
    """Raised when job execution exceeds configured deadline timeout."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=504)


class DuplicateJobError(PreprocessingBaseException):
    """Raised when a job with identical idempotency key is already processing or completed."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=409)
