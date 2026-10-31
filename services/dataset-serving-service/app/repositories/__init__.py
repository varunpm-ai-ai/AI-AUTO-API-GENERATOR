from app.repositories.base import IDatasetRepository
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.cached_repository import CachedDatasetRepository

# Global configured repository instance
dataset_repository = CachedDatasetRepository(DatasetRepository())

__all__ = [
    "IDatasetRepository",
    "DatasetRepository",
    "CachedDatasetRepository",
    "dataset_repository"
]
