from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.handlers.base import BaseRegistrationHandler
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.constants import LifecycleState
from app.logger import logger


class ReRegistrationHandler(BaseRegistrationHandler):
    async def register(
        self,
        db: AsyncSession,
        payload: Dict[str, Any],
        matched_dataset: Dataset = None
    ) -> Tuple[Dataset, DatasetVersion]:
        if not matched_dataset:
            raise ValueError("Matched dataset must be provided for ReRegistrationHandler")

        checksum = payload.get("checksum")

        # Find existing version with matching checksum or get latest version
        query = (
            select(DatasetVersion)
            .where(
                DatasetVersion.dataset_id == matched_dataset.dataset_id,
                DatasetVersion.checksum == checksum
            )
            .limit(1)
        )
        res = await db.execute(query)
        existing_version = res.scalar_one_or_none()

        if existing_version:
            # Re-registering existing version - reset status to RAW_REGISTERED for re-processing if needed
            existing_version.status = LifecycleState.RAW_REGISTERED.value
            await db.flush()
            logger.info(
                f"Re-registered existing version {existing_version.version_number} for dataset '{matched_dataset.name}'."
            )
            return matched_dataset, existing_version

        # Fallback to existing dataset handler if version wasn't found
        from app.handlers.existing_dataset_handler import ExistingDatasetHandler
        return await ExistingDatasetHandler().register(db, payload, matched_dataset)
