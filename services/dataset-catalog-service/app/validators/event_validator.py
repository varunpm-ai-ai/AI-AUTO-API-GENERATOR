from typing import Tuple, Dict, Any
from app.validators.base import BaseValidator


class EventValidator(BaseValidator):
    def validate(self, payload: Dict[str, Any]) -> Tuple[bool, str]:
        required_fields = ["event_id", "dataset_name", "source", "storage_ref", "checksum"]
        for field in required_fields:
            if not payload.get(field):
                return False, f"Missing required event field: {field}"
        return True, ""
