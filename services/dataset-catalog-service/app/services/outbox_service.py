import json
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.outbox_event import OutboxEvent
from app.constants import OutboxStatus
from app.logger import logger


class TransactionalOutbox:
    async def save_event(
        self,
        db: AsyncSession,
        event_type: str,
        payload: Dict[str, Any]
    ) -> OutboxEvent:
        serialized_payload = json.dumps(payload)
        outbox_event = OutboxEvent(
            event_type=event_type,
            payload=serialized_payload,
            status=OutboxStatus.PENDING.value
        )
        db.add(outbox_event)
        await db.flush()
        logger.info(f"Saved outbox event '{event_type}' ({outbox_event.outbox_id}) in DB transaction.")
        return outbox_event


transactional_outbox = TransactionalOutbox()
