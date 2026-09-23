from typing import Tuple, Dict, Any
from app.validators.base import BaseValidator


class SchemaValidator(BaseValidator):
    def validate(self, payload: Dict[str, Any]) -> Tuple[bool, str]:
        if not isinstance(payload, dict):
            return False, "Payload must be a dictionary"
        return True, ""
