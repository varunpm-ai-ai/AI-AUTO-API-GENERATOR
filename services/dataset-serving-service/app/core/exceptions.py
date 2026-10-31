"""
Domain Exceptions for Dataset Serving Service.
Provides typed operational exceptions with HTTP status codes and detail envelopes.
"""
from typing import Optional, Any, Dict


class ServingBaseException(Exception):
    """Base exception for all Dataset Serving errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.status_code = status_code


class DatasetNotFoundError(ServingBaseException):
    """Raised when a requested dataset ID does not exist in catalog or storage."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=404)


class VersionNotFoundError(ServingBaseException):
    """Raised when a specific dataset version is not found."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=404)


class QueryValidationError(ServingBaseException):
    """Raised when query parameters, filters, or projection columns are invalid."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=400)


class QuerySafetyError(ServingBaseException):
    """Raised when a query attempts prohibited SQL operations or violates security rules."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=403)


class RateLimitExceededError(ServingBaseException):
    """Raised when client exceeds allowed requests per window."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=429)


class QueryTimeoutError(ServingBaseException):
    """Raised when query execution exceeds allowed analytical execution deadline."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=504)


class StorageReadError(ServingBaseException):
    """Raised when accessing dataset Parquet files from object storage fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=502)


class AuthenticationError(ServingBaseException):
    """Raised when client credentials or identity tokens are invalid or missing."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=401)


class AuthorizationError(ServingBaseException):
    """Raised when client lacks permissions to read the dataset."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=403)
