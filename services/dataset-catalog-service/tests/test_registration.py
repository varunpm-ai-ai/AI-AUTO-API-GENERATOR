import pytest
from app.services.identity_resolution_service import identity_resolution_manager
from app.services.duplicate_detection_service import duplicate_detector
from app.services.dataset_registration_service import dataset_registration_manager
from app.handlers import RegistrationFactory, NewDatasetHandler, ExistingDatasetHandler
from app.constants import RegistrationType, LifecycleState


@pytest.mark.asyncio
async def test_identity_resolution_and_registration(db_session):
    payload = {
        "name": "customer_churn",
        "description": "Telecom customer churn dataset",
        "domain": "telecom",
        "source": "kaggle",
        "checksum": "checksum_v1_hash_999",
        "storage_ref": "s3://bucket/churn_v1.csv",
        "storage_type": "object_storage",
        "file_size": 1024500,
        "metadata": {"format": "csv", "rows": 7043}
    }

    # 1. Resolve identity on empty DB -> Expect non-existing
    is_ext, matched, strategy = await identity_resolution_manager.resolve_identity(db_session, payload)
    assert is_ext is False
    assert matched is None
    assert strategy == "none"

    # 2. Register dataset -> Expect new dataset created
    dataset, version = await dataset_registration_manager.register_dataset(db_session, payload)
    assert dataset.dataset_id is not None
    assert dataset.name == "customer_churn"
    assert version.version_number == 1
    assert version.checksum == "checksum_v1_hash_999"
    assert version.status == LifecycleState.RAW_REGISTERED.value

    # 3. Resolve identity after registration -> Expect exact match
    is_ext2, matched2, strategy2 = await identity_resolution_manager.resolve_identity(db_session, payload)
    assert is_ext2 is True
    assert matched2.dataset_id == dataset.dataset_id
    assert strategy2 == "exact_match"


@pytest.mark.asyncio
async def test_duplicate_detection(db_session):
    payload = {
        "name": "fraud_detection",
        "domain": "finance",
        "source": "stripe",
        "checksum": "fraud_hash_88888",
        "storage_ref": "s3://bucket/fraud.csv"
    }

    # Check duplicate on empty DB -> Expect False
    is_dup, d_id, v_id = await duplicate_detector.check_duplicate(db_session, payload)
    assert is_dup is False

    # Register dataset
    dataset, version = await dataset_registration_manager.register_dataset(db_session, payload)

    # Check duplicate again -> Expect True
    is_dup2, d_id2, v_id2 = await duplicate_detector.check_duplicate(db_session, payload)
    assert is_dup2 is True
    assert d_id2 == dataset.dataset_id
    assert v_id2 == version.version_id


@pytest.mark.asyncio
async def test_existing_dataset_new_version_registration(db_session):
    payload_v1 = {
        "name": "stock_prices",
        "domain": "finance",
        "source": "nasdaq",
        "checksum": "stock_checksum_v1",
        "storage_ref": "s3://bucket/stocks_2025.csv"
    }
    dataset1, version1 = await dataset_registration_manager.register_dataset(db_session, payload_v1)
    assert version1.version_number == 1

    payload_v2 = {
        "name": "stock_prices",
        "domain": "finance",
        "source": "nasdaq",
        "checksum": "stock_checksum_v2",
        "storage_ref": "s3://bucket/stocks_2026.csv"
    }
    dataset2, version2 = await dataset_registration_manager.register_dataset(db_session, payload_v2)
    assert dataset2.dataset_id == dataset1.dataset_id
    assert version2.version_number == 2
    assert version2.checksum == "stock_checksum_v2"
