from typing import Tuple, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.dataset import Dataset
from app.logger import logger


class IdentityResolutionManager:
    async def resolve_identity(
        self,
        db: AsyncSession,
        payload: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dataset], str]:
        """
        Resolves dataset identity.
        Returns:
            Tuple[is_existing, matched_dataset, matched_by_strategy]
        """
        name = payload.get("name") or payload.get("dataset_name")
        source = payload.get("source")
        domain = payload.get("domain")

        if not name or not source:
            return False, None, "none"

        # 1. Exact match by source, name, and domain
        query = select(Dataset).where(
            Dataset.source == source,
            Dataset.name == name,
            Dataset.domain == domain
        )
        res = await db.execute(query)
        dataset = res.scalar_one_or_none()
        if dataset:
            logger.info(f"Identity resolved: Exact match for dataset '{name}' ({dataset.dataset_id}).")
            return True, dataset, "exact_match"

        # 2. Match by source and name
        query = select(Dataset).where(
            Dataset.source == source,
            Dataset.name == name
        )
        res = await db.execute(query)
        dataset = res.scalar_one_or_none()
        if dataset:
            logger.info(f"Identity resolved: Source + Name match for dataset '{name}' ({dataset.dataset_id}).")
            return True, dataset, "source_name_match"

        logger.info(f"Identity resolved: No existing dataset match found for '{name}' from source '{source}'.")
        return False, None, "none"


identity_resolution_manager = IdentityResolutionManager()
