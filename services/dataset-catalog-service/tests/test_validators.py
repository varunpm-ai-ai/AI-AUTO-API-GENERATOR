import pytest
from app.validators import (
    ValidationFactory,
    ValidationManager,
    EventValidator,
    SchemaValidator,
    MetadataValidator,
    VersionValidator,
    IdentityValidator
)


def test_validation_factory():
    event_v = ValidationFactory.get_validator("event")
    assert isinstance(event_v, EventValidator)

    identity_v = ValidationFactory.get_validator("identity")
    assert isinstance(identity_v, IdentityValidator)

    with pytest.raises(ValueError):
        ValidationFactory.get_validator("non_existent_validator")


def test_event_validator():
    validator = EventValidator()
    valid_payload = {
        "event_id": "evt-123",
        "dataset_name": "titanic",
        "source": "kaggle",
        "storage_ref": "s3://bucket/titanic.csv",
        "checksum": "abc12345"
    }
    is_valid, err = validator.validate(valid_payload)
    assert is_valid is True
    assert err == ""

    invalid_payload = {"event_id": "evt-123"}
    is_valid, err = validator.validate(invalid_payload)
    assert is_valid is False
    assert "Missing required event field" in err


def test_identity_validator():
    validator = IdentityValidator()
    valid_payload = {
        "name": "sales_data",
        "source": "internal_db",
        "domain": "finance"
    }
    is_valid, err = validator.validate(valid_payload)
    assert is_valid is True

    missing_name = {"source": "internal_db", "domain": "finance"}
    is_valid, err = validator.validate(missing_name)
    assert is_valid is False
    assert "name is required" in err


def test_version_validator():
    validator = VersionValidator()
    valid = {"checksum": "12345678", "storage_ref": "s3://b/f.csv"}
    assert validator.validate(valid)[0] is True

    invalid = {"checksum": "12"}
    assert validator.validate(invalid)[0] is False


def test_validation_manager():
    mgr = ValidationManager()
    payload = {
        "name": "user_logs",
        "source": "web",
        "domain": "analytics",
        "checksum": "sha256_hash_123",
        "storage_ref": "s3://b/logs.csv"
    }
    is_valid, err = mgr.validate(payload, ["identity", "version", "schema"])
    assert is_valid is True
    assert err == ""
