import logging
import json
import sys
from contextvars import ContextVar
from typing import Any, Dict
from datetime import datetime, timezone
from app.config.settings import settings

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="SYSTEM")


class JSONFormatter(logging.Formatter):
    """
    Formats log records as structured single-line JSON with timestamps,
    log levels, service metadata, and correlation IDs.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": settings.SERVICE_NAME,
            "logger": record.name,
            "correlation_id": correlation_id_ctx.get(),
            "message": record.getMessage()
        }

        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_data.update(record.extra)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """Configures and retrieves a logger instance using structured JSON formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
    return logger
