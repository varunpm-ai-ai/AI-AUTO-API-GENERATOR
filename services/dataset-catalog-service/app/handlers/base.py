from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion


class BaseRegistrationHandler(ABC):
    @abstractmethod
    async def register(
        self,
        db: AsyncSession,
        payload: Dict[str, Any],
        matched_dataset: Dataset = None
    ) -> Tuple[Dataset, DatasetVersion]:
        """
        Executes registration strategy.
        Returns:
            Tuple[Dataset, DatasetVersion]
        """
        pass
