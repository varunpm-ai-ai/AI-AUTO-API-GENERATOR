"""
Command Pattern Interface.
Encapsulates an executable job command with lifecycle hooks and state inspection.
"""
from abc import ABC, abstractmethod
from app.schemas.job import JobStatus, JobResultResponse


class IJobCommand(ABC):
    """Abstract Command for managing preprocessing task execution."""

    @abstractmethod
    def execute(self) -> JobResultResponse:
        """Executes the command and returns the final job result."""
        pass

    @abstractmethod
    def abort(self, reason: str) -> None:
        """Signals cancellation to the running command."""
        pass

    @abstractmethod
    def get_status(self) -> JobStatus:
        """Returns the current execution status."""
        pass
