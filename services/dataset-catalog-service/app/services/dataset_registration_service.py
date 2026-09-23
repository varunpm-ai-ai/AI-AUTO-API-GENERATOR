from typing import Dict, Any, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.validators.manager import validation_manager
from app.services.identity_resolution_service import identity_resolution_manager
from app.services.duplicate_detection_service import duplicate_detector
from app.handlers.factory import RegistrationFactory
from app.constants import RegistrationType, Topics, LifecycleState
from app.services.metadata_service import metadata_manager
from app.services.lifecycle_service import lifecycle_manager
from app.services.outbox_service import transactional_outbox
from app.services.preprocessing_publisher import preprocessing_job_publisher
from app.logger import logger


class DatasetRegistrationManager:
    async def register_dataset(
        self,
        db: AsyncSession,
        payload: Dict[str, Any],
        force_re_registration: bool = False
    ) -> Tuple[Dataset, DatasetVersion]:
        # 1. Validation Manager -> Validate request schema, event, version, identity
        is_valid, err = validation_manager.validate(
            payload, ["identity", "version", "metadata"]
        )
        if not is_valid:
            raise ValueError(f"Registration validation failed: {err}")

        # 2. Identity Resolution Manager -> Resolve logical dataset identity
        is_existing, matched_dataset, match_strategy = await identity_resolution_manager.resolve_identity(
            db, payload
        )

        # 3. Duplicate Detector -> Check for duplicate content
        is_duplicate, dup_dataset_id, dup_version_id = await duplicate_detector.check_duplicate(
            db, payload
        )

        if is_duplicate and not force_re_registration:
            logger.info(f"Prevented duplicate registration for checksum {payload.get('checksum')}.")
            # If dataset exists, load and return existing
            if is_existing and matched_dataset:
                query_ver = await db.execute(
                    matched_dataset.versions.select().where(DatasetVersion.version_id == dup_version_id)
                ) if hasattr(matched_dataset.versions, "select") else None
                # Fetch existing version
                from app.services.version_service import version_manager
                dup_version = await version_manager.get_version_by_id(db, dup_version_id)
                if dup_version:
                    return matched_dataset, dup_version
            raise ValueError(f"Duplicate dataset version detected (checksum: {payload.get('checksum')})")

        # 4. Determine Registration Handler via RegistrationFactory
        if force_re_registration and is_existing:
            reg_type = RegistrationType.RE_REGISTRATION
        elif is_existing:
            reg_type = RegistrationType.EXISTING
        else:
            reg_type = RegistrationType.NEW

        handler = RegistrationFactory.get_handler(reg_type)
        dataset, version = await handler.register(db, payload, matched_dataset)

        # 5. Metadata Manager -> Extract and persist initial metadata
        await metadata_manager.save_metadata(db, version, payload, source="registration")

        # 6. Lifecycle Manager -> Set status to RAW_REGISTERED
        await lifecycle_manager.transition_state(db, version, LifecycleState.RAW_REGISTERED)

        # 7. Transactional Outbox -> Record DATASET_REGISTERED event
        outbox_payload = {
            "dataset_id": dataset.dataset_id,
            "version_id": version.version_id,
            "name": dataset.name,
            "domain": dataset.domain,
            "source": dataset.source,
            "checksum": version.checksum,
            "storage_ref": version.storage_ref,
            "status": version.status
        }
        await transactional_outbox.save_event(db, Topics.DATASET_REGISTERED, outbox_payload)

        # Commit DB transaction
        await db.commit()
        await db.refresh(dataset)
        await db.refresh(version)

        # 8. Preprocessing Job Publisher -> Publish preprocessing job to RabbitMQ
        await preprocessing_job_publisher.publish_job(
            dataset_id=dataset.dataset_id,
            version_id=version.version_id,
            storage_ref=version.storage_ref,
            checksum=version.checksum
        )

        return dataset, version


dataset_registration_manager = DatasetRegistrationManager()
