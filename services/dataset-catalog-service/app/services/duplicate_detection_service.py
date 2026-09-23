from typing import Tuple, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.dataset_version import DatasetVersion
from app.logger import logger


class DuplicateDetector:
    async def check_duplicate(
        self,
        db: AsyncSession,
        payload: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Checks for duplicate dataset versions by checksum and storage reference.
        Returns:
            Tuple[is_duplicate, existing_dataset_id, existing_version_id]
        """
        checksum = payload.get("checksum")
        storage_ref = payload.get("storage_ref")

        if not checksum:
            return False, None, None

        # Check by checksum
        query = select(DatasetVersion).where(DatasetVersion.checksum == checksum)
        res = await db.execute(query)
        version = res.scalar_one_or_none()

        if version:
            logger.info(
                f"Duplicate detected by checksum ({checksum}): dataset_id={version.dataset_id}, version_id={version.version_id}."
            )
            return True, version.dataset_id, version.version_id

        # Check by storage reference if provided
        if storage_ref:
            query = select(DatasetVersion).where(DatasetVersion.storage_ref == storage_ref)
            res = await db.execute(query)
            version = res.scalar_one_or_none()

            if version:
                logger.info(
                    f"Duplicate detected by storage_ref ({storage_ref}): dataset_id={version.dataset_id}, version_id={version.version_id}."
                )
                return True, version.dataset_id, version.version_id

        return False, None, None


duplicate_detector = DuplicateDetector()
