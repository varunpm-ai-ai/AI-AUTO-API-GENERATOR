import json
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aiokafka import AIOKafkaProducer
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.outbox_event import OutboxEvent
from app.constants import OutboxStatus
from app.logger import logger


class EventPublisher:
    def __init__(self):
        self.producer = None
        self._running = False

    async def connect(self):
        try:
            producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            await producer.start()
            self.producer = producer
            logger.info("Kafka EventPublisher connected successfully.")
        except Exception as e:
            logger.warning(f"Kafka producer connection failed ({e}). Running EventPublisher in simulated mode.")
            self.producer = None

    async def publish_outbox_events(self, db: AsyncSession):
        query = (
            select(OutboxEvent)
            .where(OutboxEvent.status == OutboxStatus.PENDING.value)
            .order_by(OutboxEvent.created_at.asc())
            .limit(50)
        )
        res = await db.execute(query)
        pending_events = res.scalars().all()

        for event in pending_events:
            try:
                payload = json.loads(event.payload)
                topic = event.event_type

                if self.producer:
                    await self.producer.send_and_wait(topic, payload)
                    logger.info(f"Published outbox event '{event.outbox_id}' to Kafka topic '{topic}'.")
                else:
                    logger.info(f"[SIMULATED KAFKA] Published outbox event '{event.outbox_id}' to topic '{topic}'.")

                event.status = OutboxStatus.PUBLISHED.value
                event.published_at = datetime.utcnow()
            except Exception as e:
                logger.error(f"Error publishing outbox event '{event.outbox_id}': {e}")
                event.status = OutboxStatus.FAILED.value

        await db.commit()

    async def start_worker(self, interval_seconds: int = 5):
        self._running = True
        await self.connect()

        while self._running:
            try:
                async with AsyncSessionLocal() as db:
                    await self.publish_outbox_events(db)
            except Exception as e:
                logger.error(f"Error in EventPublisher worker loop: {e}")
            await asyncio.sleep(interval_seconds)

    async def stop(self):
        self._running = False
        if self.producer:
            await self.producer.stop()


event_publisher = EventPublisher()
