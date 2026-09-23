from typing import Tuple, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.dataset_version import DatasetVersion
from app.models.processing_status import ProcessingStatus
from app.constants import LifecycleState
from app.logger import logger


class LifecycleManager:
    # Valid state transition rules
    VALID_TRANSITIONS = {
        LifecycleState.RAW_REGISTERED: [LifecycleState.PROCESSING, LifecycleState.FAILED],
        LifecycleState.PROCESSING: [LifecycleState.READY, LifecycleState.FAILED],
        LifecycleState.READY: [LifecycleState.PROCESSING],  # Allow re-processing if needed
        LifecycleState.FAILED: [LifecycleState.RAW_REGISTERED, LifecycleState.PROCESSING]
    }

    async def transition_state(
        self,
        db: AsyncSession,
        version: DatasetVersion,
        new_state: LifecycleState,
        error_message: Optional[str] = None
    ) -> Tuple[bool, str]:
        current_state = LifecycleState(version.status)

        if new_state not in self.VALID_TRANSITIONS.get(current_state, []):
            msg = f"Invalid state transition from '{current_state.value}' to '{new_state.value}'"
            logger.warning(msg)
            return False, msg

        # Update version status
        version.status = new_state.value

        # Create processing status history record
        status_record = ProcessingStatus(
            version_id=version.version_id,
            state=new_state.value,
            error_message=error_message,
            processed_at=datetime.utcnow()
        )
        db.add(status_record)
        await db.flush()

        logger.info(
            f"Transitioned version '{version.version_id}' state: {current_state.value} -> {new_state.value}"
        )
        return True, ""


lifecycle_manager = LifecycleManager()
