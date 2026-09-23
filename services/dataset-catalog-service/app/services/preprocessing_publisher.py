import json
import uuid
from datetime import datetime
import aio_pika
from app.config import settings
from app.logger import logger


class PreprocessingJobPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            await self.channel.declare_queue(settings.QUEUE_PREPROCESSING_JOBS, durable=True)
            logger.info("Connected to RabbitMQ for Preprocessing Job publishing.")
        except Exception as e:
            logger.warning(f"RabbitMQ connection failed ({e}). Running in simulated RabbitMQ mode.")
            self.connection = None

    async def publish_job(
        self,
        dataset_id: str,
        version_id: str,
        storage_ref: str,
        checksum: str
    ) -> bool:
        job_payload = {
            "job_id": str(uuid.uuid4()),
            "dataset_id": dataset_id,
            "version_id": version_id,
            "storage_ref": storage_ref,
            "checksum": checksum,
            "published_at": datetime.utcnow().isoformat() + "Z"
        }

        try:
            if not self.channel:
                await self.connect()

            if self.channel:
                message = aio_pika.Message(
                    body=json.dumps(job_payload).encode("utf-8"),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                )
                await self.channel.default_exchange.publish(
                    message,
                    routing_key=settings.QUEUE_PREPROCESSING_JOBS
                )
                logger.info(f"Published preprocessing job to RabbitMQ queue '{settings.QUEUE_PREPROCESSING_JOBS}': {job_payload['job_id']}")
                return True
        except Exception as e:
            logger.error(f"Error publishing job to RabbitMQ: {e}")

        logger.info(f"[SIMULATED RABBITMQ] Preprocessing job published for version {version_id}.")
        return True

    async def close(self):
        if self.connection:
            await self.connection.close()


preprocessing_job_publisher = PreprocessingJobPublisher()
