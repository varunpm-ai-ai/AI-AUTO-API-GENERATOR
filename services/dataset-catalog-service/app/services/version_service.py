from typing import Tuple, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.dataset_version import DatasetVersion
from app.validators.manager import validation_manager
from app.logger import logger


class VersionManager:
    async def validate_version(self, payload: dict) -> Tuple[bool, str]:
        return validation_manager.validate(payload, ["version"])

    async def get_version_by_id(
        self,
        db: AsyncSession,
        version_id: str
    ) -> Optional[DatasetVersion]:
        query = select(DatasetVersion).where(DatasetVersion.version_id == version_id)
        res = await db.execute(query)
        return res.scalar_one_or_none()

    async def get_versions_for_dataset(
        self,
        db: AsyncSession,
        dataset_id: str
    ) -> List[DatasetVersion]:
        query = (
            select(DatasetVersion)
            .where(DatasetVersion.dataset_id == dataset_id)
            .order_by(DatasetVersion.version_number.desc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())


version_manager = VersionManager()
