from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.handlers.base import BaseRegistrationHandler
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.storage_reference import StorageReference
from app.constants import LifecycleState
from app.logger import logger


class ExistingDatasetHandler(BaseRegistrationHandler):
    async def register(
        self,
        db: AsyncSession,
        payload: Dict[str, Any],
        matched_dataset: Dataset = None
    ) -> Tuple[Dataset, DatasetVersion]:
        if not matched_dataset:
            raise ValueError("Matched dataset must be provided for ExistingDatasetHandler")

        checksum = payload.get("checksum")
        storage_ref = payload.get("storage_ref")
        storage_type = payload.get("storage_type", "object_storage")
        file_size = payload.get("file_size", 0)

        # Get max version_number for this dataset
        query = select(func.max(DatasetVersion.version_number)).where(
            DatasetVersion.dataset_id == matched_dataset.dataset_id
        )
        res = await db.execute(query)
        max_ver = res.scalar() or 0
        next_ver = max_ver + 1

        # Create new DatasetVersion
        version = DatasetVersion(
            dataset_id=matched_dataset.dataset_id,
            version_number=next_ver,
            checksum=checksum,
            storage_ref=storage_ref,
            status=LifecycleState.RAW_REGISTERED.value
        )
        db.add(version)
        await db.flush()

        # Create StorageReference
        storage = StorageReference(
            version_id=version.version_id,
            uri=storage_ref,
            storage_type=storage_type,
            file_size=file_size,
            checksum=checksum
        )
        db.add(storage)
        await db.flush()

        logger.info(
            f"Added version {next_ver} ({version.version_id}) to existing dataset '{matched_dataset.name}' ({matched_dataset.dataset_id})."
        )
        return matched_dataset, version
