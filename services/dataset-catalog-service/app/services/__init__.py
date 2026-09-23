from app.services.identity_resolution_service import IdentityResolutionManager, identity_resolution_manager
from app.services.duplicate_detection_service import DuplicateDetector, duplicate_detector
from app.services.dataset_registration_service import DatasetRegistrationManager, dataset_registration_manager
from app.services.version_service import VersionManager, version_manager
from app.services.metadata_service import MetadataManager, metadata_manager
from app.services.lifecycle_service import LifecycleManager, lifecycle_manager
from app.services.preprocessing_publisher import PreprocessingJobPublisher, preprocessing_job_publisher
from app.services.preprocessing_consumer import PreprocessingResultConsumer, preprocessing_result_consumer
from app.services.outbox_service import TransactionalOutbox, transactional_outbox
from app.services.event_publisher_service import EventPublisher, event_publisher
from app.services.kafka_consumer_service import KafkaConsumerService, kafka_consumer_service

__all__ = [
    "IdentityResolutionManager",
    "identity_resolution_manager",
    "DuplicateDetector",
    "duplicate_detector",
    "DatasetRegistrationManager",
    "dataset_registration_manager",
    "VersionManager",
    "version_manager",
    "MetadataManager",
    "metadata_manager",
    "LifecycleManager",
    "lifecycle_manager",
    "PreprocessingJobPublisher",
    "preprocessing_job_publisher",
    "PreprocessingResultConsumer",
    "preprocessing_result_consumer",
    "TransactionalOutbox",
    "transactional_outbox",
    "EventPublisher",
    "event_publisher",
    "KafkaConsumerService",
    "kafka_consumer_service",
]
