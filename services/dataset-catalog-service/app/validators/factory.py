from app.validators.base import BaseValidator
from app.validators.event_validator import EventValidator
from app.validators.schema_validator import SchemaValidator
from app.validators.metadata_validator import MetadataValidator
from app.validators.version_validator import VersionValidator
from app.validators.identity_validator import IdentityValidator


class ValidationFactory:
    _validators = {
        "event": EventValidator(),
        "schema": SchemaValidator(),
        "metadata": MetadataValidator(),
        "version": VersionValidator(),
        "identity": IdentityValidator(),
    }

    @classmethod
    def get_validator(cls, validator_type: str) -> BaseValidator:
        validator = cls._validators.get(validator_type.lower())
        if not validator:
            raise ValueError(f"Unknown validator type: {validator_type}")
        return validator
