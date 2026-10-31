"""
RabbitMQ Asynchronous Consumer.
Handles message consumption, bounded prefetch concurrency, validation, retry tracking, and DLQ routing.
"""
from typing import Optional
import json
import asyncio
import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from app.config.settings import settings
from app.config.logger import get_logger
from app.schemas.job import JobRequestPayload, JobStatus
from app.messaging.kafka_producer import kafka_publisher

logger = get_logger(__name__)


class RabbitMQConsumer:
    """Asynchronous AMQP worker consuming preprocessing jobs."""

    def __init__(self):
        self.amqp_url = settings.RABBITMQ_URL
        self.queue_name = settings.RABBITMQ_QUEUE
        self.dlq_name = settings.RABBITMQ_DLQ
        self.prefetch = settings.RABBITMQ_PREFETCH_COUNT
        self.max_retries = settings.RABBITMQ_MAX_RETRIES
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.RobustChannel] = None
        self.is_running = False

    async def start(self) -> None:
        """Connects to RabbitMQ broker and initiates the consumption loop."""
        try:
            self.connection = await aio_pika.connect_robust(self.amqp_url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=self.prefetch)

            # Declare primary queue and dead letter queue
            queue = await self.channel.declare_queue(self.queue_name, durable=True)
            await self.channel.declare_queue(self.dlq_name, durable=True)

            self.is_running = True
            await queue.consume(self.process_message)
            logger.info(f"RabbitMQ consumer listening on queue '{self.queue_name}' with prefetch={self.prefetch}")

        except Exception as e:
            logger.warning(f"Could not connect to RabbitMQ ({e}). Service running in HTTP-trigger mode.")
            self.is_running = False

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        """Processes an individual inbound AMQP message."""
        async with message.process(requeue=False, ignore_processed=True):
            body_text = message.body.decode("utf-8")
            logger.info(f"Received AMQP message from queue '{self.queue_name}'")

            try:
                # 1. Deserialize payload
                payload_dict = json.loads(body_text)
                job_payload = JobRequestPayload.model_validate(payload_dict)

                # 2. Run command asynchronously in executor to prevent blocking the event loop
                from app.commands.preprocess_command import PreprocessingJobCommand
                command = PreprocessingJobCommand(job_payload)
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, command.execute)

                # 3. Handle outcomes and Kafka publication
                if result.status == JobStatus.COMPLETED:
                    await kafka_publisher.publish_preprocessed_event(result.model_dump())
                    await message.ack()
                    logger.info(f"Job {result.job_id} successfully processed and ACKed")
                else:
                    await self._handle_failure(message, result.error_message or "Unknown error", job_payload)

            except Exception as e:
                logger.error(f"Error processing AMQP message: {e}", exc_info=True)
                await self._handle_failure(message, str(e))

    async def _handle_failure(
        self,
        message: AbstractIncomingMessage,
        error_msg: str,
        payload: Optional[JobRequestPayload] = None
    ) -> None:
        """Inspects retry count and routes to DLQ if max retries exceeded."""
        headers = message.headers or {}
        retry_count = int(headers.get("x-retry-count", 0)) + 1

        if retry_count <= self.max_retries:
            logger.warning(f"Job retry {retry_count}/{self.max_retries}. Requeuing with backoff.")
            # Publish back to primary queue with incremented retry header
            if self.channel:
                await self.channel.default_exchange.publish(
                    aio_pika.Message(
                        body=message.body,
                        headers={**headers, "x-retry-count": retry_count},
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    ),
                    routing_key=self.queue_name
                )
            await message.ack()
        else:
            logger.error(f"Job exceeded max retries ({self.max_retries}). Routing to DLQ '{self.dlq_name}'.")
            if self.channel:
                await self.channel.default_exchange.publish(
                    aio_pika.Message(
                        body=message.body,
                        headers={**headers, "x-death-reason": error_msg},
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    ),
                    routing_key=self.dlq_name
                )
            if payload:
                await kafka_publisher.publish_failed_event({
                    "job_id": payload.job_id,
                    "dataset_id": payload.dataset_id,
                    "error": error_msg,
                    "status": "FAILED_DLQ"
                })
            await message.ack()

    async def stop(self) -> None:
        """Closes AMQP channel and connection."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("RabbitMQ consumer stopped.")


rabbitmq_consumer = RabbitMQConsumer()
