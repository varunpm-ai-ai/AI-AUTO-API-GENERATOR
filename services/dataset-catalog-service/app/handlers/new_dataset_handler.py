from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.base import BaseRegistrationHandler
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.storage_reference import StorageReference
from app.constants import LifecycleState
from app.logger import logger


class NewDatasetHandler(BaseRegistrationHandler):
    async def register(
        self,
        db: AsyncSession,
        payload: Dict[str, Any],
        matched_dataset: Dataset = None
    ) -> Tuple[Dataset, DatasetVersion]:
        name = payload.get("name") or payload.get("dataset_name")
        description = payload.get("description", "")
        domain = payload.get("domain")
        source = payload.get("source")
        checksum = payload.get("checksum")
        storage_ref = payload.get("storage_ref")
        storage_type = payload.get("storage_type", "object_storage")
        file_size = payload.get("file_size", 0)

        # Create new Dataset record
        dataset = Dataset(
            name=name,
            description=description,
            domain=domain,
            source=source
        )
        db.add(dataset)
        await db.flush()

        # Create first DatasetVersion (v1)
        version = DatasetVersion(
            dataset_id=dataset.dataset_id,
            version_number=1,
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

        logger.info(f"Registered new dataset '{name}' ({dataset.dataset_id}) with version 1 ({version.version_id}).")
        return dataset, version
