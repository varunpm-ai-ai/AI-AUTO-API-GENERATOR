import json
import asyncio
from typing import Dict, Any
from aiokafka import AIOKafkaConsumer
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.dataset_event import DatasetEvent
from app.validators.manager import validation_manager
from app.services.dataset_registration_service import dataset_registration_manager
from app.constants import EventStatus
from app.logger import logger


class KafkaConsumerService:
    """Singleton Kafka Consumer for listening to upstream dataset events."""
    def __init__(self):
        self.consumer = None
        self._running = False

    async def connect(self):
        try:
            consumer = AIOKafkaConsumer(
                settings.TOPIC_DATASET_ACQUIRED,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id="dataset-catalog-service-group",
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest"
            )
            await consumer.start()
            self.consumer = consumer
            logger.info(f"KafkaConsumerService subscribed to topic '{settings.TOPIC_DATASET_ACQUIRED}'.")
        except Exception as e:
            logger.warning(f"Kafka consumer connection failed ({e}). Running KafkaConsumer in standby mode.")
            self.consumer = None

    async def process_event(self, payload: Dict[str, Any]) -> bool:
        # Validate event payload via ValidationManager
        is_valid, err = validation_manager.validate(payload, ["event"])
        if not is_valid:
            logger.error(f"Kafka consumer received invalid event payload: {err}")
            return False

        async with AsyncSessionLocal() as db:
            # Record idempotency / event log
            event_log = DatasetEvent(
                event_type=settings.TOPIC_DATASET_ACQUIRED,
                source_service="discovery-service",
                payload=json.dumps(payload),
                status=EventStatus.RECEIVED.value
            )
            db.add(event_log)
            await db.flush()

            try:
                # Perform dataset registration workflow
                await dataset_registration_manager.register_dataset(db, payload)
                event_log.status = EventStatus.PROCESSED.value
                await db.commit()
                logger.info(f"Successfully processed acquired dataset event from Kafka.")
                return True
            except Exception as e:
                logger.error(f"Error processing acquired dataset event: {e}")
                event_log.status = EventStatus.FAILED.value
                await db.commit()
                return False

    async def start_listening(self):
        self._running = True
        await self.connect()

        if not self.consumer:
            logger.info("Kafka consumer offline. Waiting for manual/API event triggers.")
            return

        try:
            async for msg in self.consumer:
                if not self._running:
                    break
                logger.info(f"Received Kafka message from topic '{msg.topic}'")
                await self.process_event(msg.value)
        except Exception as e:
            logger.error(f"Error in Kafka consumer loop: {e}")

    async def stop(self):
        self._running = False
        if self.consumer:
            await self.consumer.stop()


kafka_consumer_service = KafkaConsumerService()
