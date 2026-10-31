"""
Pipeline Stage Interface (Pipeline / Chain of Responsibility Pattern).
Defines the standard execution contract for each transformation stage in the preprocessing workflow.
"""
from abc import ABC, abstractmethod
from app.core.context import PipelineContext


class IPipelineStage(ABC):
    """Abstract stage in the preprocessing chain."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the stage for metrics and tracing."""
        pass

    @abstractmethod
    def execute(self, context: PipelineContext) -> None:
        """
        Executes the stage logic against the shared PipelineContext.
        Mutates the context with intermediate artifacts and metadata.
        """
        pass
