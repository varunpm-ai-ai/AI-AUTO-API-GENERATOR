import pytest
from sqlalchemy import select
from app.services.dataset_registration_service import dataset_registration_manager
from app.services.lifecycle_service import lifecycle_manager
from app.services.metadata_service import metadata_manager
from app.services.outbox_service import transactional_outbox
from app.services.preprocessing_consumer import preprocessing_result_consumer
from app.models.outbox_event import OutboxEvent
from app.constants import LifecycleState, Topics


@pytest.mark.asyncio
async def test_lifecycle_state_transitions(db_session):
    payload = {
        "name": "sensor_readings",
        "domain": "iot",
        "source": "factory_sensor_1",
        "checksum": "sensor_checksum_101",
        "storage_ref": "s3://iot/sensor_1.parquet"
    }

    dataset, version = await dataset_registration_manager.register_dataset(db_session, payload)
    assert version.status == LifecycleState.RAW_REGISTERED.value

    # Transition RAW_REGISTERED -> PROCESSING
    success, err = await lifecycle_manager.transition_state(db_session, version, LifecycleState.PROCESSING)
    assert success is True
    assert version.status == LifecycleState.PROCESSING.value

    # Transition PROCESSING -> READY
    success2, err2 = await lifecycle_manager.transition_state(db_session, version, LifecycleState.READY)
    assert success2 is True
    assert version.status == LifecycleState.READY.value

    # Test invalid transition: READY -> RAW_REGISTERED (Invalid state machine path)
    success3, err3 = await lifecycle_manager.transition_state(db_session, version, LifecycleState.RAW_REGISTERED)
    assert success3 is False
    assert "Invalid state transition" in err3


@pytest.mark.asyncio
async def test_preprocessing_result_consumption(db_session):
    payload = {
        "name": "weather_data",
        "domain": "climate",
        "source": "noaa",
        "checksum": "weather_checksum_555",
        "storage_ref": "s3://noaa/2026.csv"
    }

    dataset, version = await dataset_registration_manager.register_dataset(db_session, payload)

    # Consume COMPLETED result
    result_payload = {
        "job_id": "job-abc-123",
        "dataset_id": dataset.dataset_id,
        "version_id": version.version_id,
        "status": "COMPLETED",
        "extracted_metadata": {"column_count": 14, "row_count": 50000},
        "completed_at": "2026-09-23T12:00:00Z"
    }

    success = await preprocessing_result_consumer.handle_processing_result(db_session, result_payload)
    assert success is True
    assert version.status == LifecycleState.READY.value

    # Verify outbox event DATASET_READY was written
    query = select(OutboxEvent).where(OutboxEvent.event_type == Topics.DATASET_READY)
    res = await db_session.execute(query)
    outbox_evt = res.scalar_one_or_none()
    assert outbox_evt is not None
    assert version.version_id in outbox_evt.payload
