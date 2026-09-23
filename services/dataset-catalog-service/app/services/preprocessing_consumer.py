import json
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dataset_version import DatasetVersion
from app.services.lifecycle_service import lifecycle_manager
from app.services.metadata_service import metadata_manager
from app.services.outbox_service import transactional_outbox
from app.services.version_service import version_manager
from app.constants import LifecycleState, Topics
from app.logger import logger


class PreprocessingResultConsumer:
    """Singleton consumer responsible for consuming preprocessing results."""

    async def handle_processing_result(
        self,
        db: AsyncSession,
        payload: Dict[str, Any]
    ) -> bool:
        version_id = payload.get("version_id")
        status = payload.get("status", "").upper()
        error_message = payload.get("error_message")
        extracted_metadata = payload.get("extracted_metadata", {})

        if not version_id:
            logger.error("Preprocessing result missing version_id.")
            return False

        version = await version_manager.get_version_by_id(db, version_id)
        if not version:
            logger.error(f"Version '{version_id}' not found for processing result handling.")
            return False

        # First transition from RAW_REGISTERED to PROCESSING if still RAW_REGISTERED
        if version.status == LifecycleState.RAW_REGISTERED.value:
            await lifecycle_manager.transition_state(db, version, LifecycleState.PROCESSING)

        if status == "COMPLETED" or status == "READY":
            # Transition state to READY
            await lifecycle_manager.transition_state(db, version, LifecycleState.READY)

            # Save extracted metadata
            if extracted_metadata:
                await metadata_manager.save_metadata(
                    db,
                    version,
                    {"metadata": extracted_metadata},
                    source="preprocessing_service"
                )

            # Record outbox event: DATASET_READY
            await transactional_outbox.save_event(
                db,
                Topics.DATASET_READY,
                {
                    "dataset_id": version.dataset_id,
                    "version_id": version.version_id,
                    "version_number": version.version_number,
                    "status": LifecycleState.READY.value
                }
            )
            logger.info(f"Successfully processed dataset version '{version_id}' -> READY.")
        else:
            # Transition state to FAILED
            await lifecycle_manager.transition_state(
                db,
                version,
                LifecycleState.FAILED,
                error_message=error_message or "Preprocessing failed"
            )

            # Record outbox event: DATASET_PROCESSING_FAILED
            await transactional_outbox.save_event(
                db,
                Topics.DATASET_PROCESSING_FAILED,
                {
                    "dataset_id": version.dataset_id,
                    "version_id": version.version_id,
                    "status": LifecycleState.FAILED.value,
                    "error_message": error_message
                }
            )
            logger.warning(f"Dataset version '{version_id}' processing failed: {error_message}")

        return True


preprocessing_result_consumer = PreprocessingResultConsumer()
