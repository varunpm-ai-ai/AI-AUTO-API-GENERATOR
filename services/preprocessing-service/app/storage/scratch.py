"""
Ephemeral Scratch Directory Manager.
Provides RAII-style scoped workspace isolation for job processing and deterministic disk cleanup.
"""
import shutil
import os
from pathlib import Path
from typing import Optional
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)


class ScratchDirectoryManager:
    """
    Manages an ephemeral local filesystem directory dedicated to a single preprocessing job.
    Guarantees cleanup on completion or failure.
    """
    def __init__(self, job_id: str, base_dir: Optional[str] = None):
        self.job_id = job_id
        self.base_dir = Path(base_dir or settings.TEMP_SCRATCH_DIR)
        self.scratch_dir = self.base_dir / f"job_{job_id}"

    def __enter__(self) -> Path:
        self.create()
        return self.scratch_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def create(self) -> Path:
        """Creates the ephemeral scratch directory."""
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Allocated scratch workspace at: {self.scratch_dir}", extra={"job_id": self.job_id})
        return self.scratch_dir

    def cleanup(self) -> None:
        """Deletes the ephemeral scratch directory and all its temporary files."""
        if self.scratch_dir.exists():
            try:
                shutil.rmtree(self.scratch_dir)
                logger.debug(f"Deallocated and cleaned scratch workspace: {self.scratch_dir}", extra={"job_id": self.job_id})
            except Exception as e:
                logger.warning(f"Failed to cleanup scratch workspace {self.scratch_dir}: {e}", extra={"job_id": self.job_id})

    def get_file_path(self, filename: str) -> Path:
        """Returns an absolute path inside the scratch directory."""
        return self.scratch_dir / filename
