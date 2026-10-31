"""
Kafka Event Publisher.
Dispatches lifecycle events (DATASET_PREPROCESSED, DATASET_PREPROCESS_FAILED)
with graceful fallback for local testing.
"""
from typing import Dict, Any, Optional
import json
import asyncio
from aiokafka import AIOKafkaProducer
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)


class KafkaEventPublisher:
    """Publishes asynchronous events for downstream pipeline microservices."""

    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.topic_preprocessed = settings.KAFKA_TOPIC_PREPROCESSED
        self.topic_failed = settings.KAFKA_TOPIC_FAILED
        self._producer: Optional[AIOKafkaProducer] = None

    async def _get_producer(self) -> Optional[AIOKafkaProducer]:
        if self._producer is None:
            try:
                producer = AIOKafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8")
                )
                await producer.start()
                self._producer = producer
            except Exception as e:
                logger.warning(f"Kafka broker connection failed ({e}). Running in offline event log mode.")
                self._producer = None
        return self._producer

    async def publish_preprocessed_event(self, payload: Dict[str, Any]) -> None:
        """Emits event indicating dataset has been successfully preprocessed."""
        producer = await self._get_producer()
        if producer:
            try:
                await producer.send_and_wait(self.topic_preprocessed, payload)
                logger.info(f"Published success event to Kafka topic '{self.topic_preprocessed}'")
            except Exception as e:
                logger.error(f"Failed to publish Kafka event to '{self.topic_preprocessed}': {e}")
        else:
            logger.info(f"[Offline Kafka] Simulated publish to '{self.topic_preprocessed}': {payload.get('job_id')}")

    async def publish_failed_event(self, payload: Dict[str, Any]) -> None:
        """Emits event indicating dataset preprocessing failed."""
        producer = await self._get_producer()
        if producer:
            try:
                await producer.send_and_wait(self.topic_failed, payload)
                logger.info(f"Published failure event to Kafka topic '{self.topic_failed}'")
            except Exception as e:
                logger.error(f"Failed to publish Kafka event to '{self.topic_failed}': {e}")
        else:
            logger.info(f"[Offline Kafka] Simulated publish to '{self.topic_failed}': {payload.get('job_id')}")

    async def stop(self) -> None:
        """Gracefully closes the Kafka producer."""
        if self._producer:
            await self._producer.stop()
            self._producer = None


kafka_publisher = KafkaEventPublisher()
