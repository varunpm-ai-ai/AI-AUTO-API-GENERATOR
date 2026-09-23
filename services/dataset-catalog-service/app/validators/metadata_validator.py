from typing import Tuple, Dict, Any
from app.validators.base import BaseValidator


class MetadataValidator(BaseValidator):
    def validate(self, payload: Dict[str, Any]) -> Tuple[bool, str]:
        metadata = payload.get("metadata", {})
        if metadata is not None and not isinstance(metadata, dict):
            return False, "Metadata must be a dictionary"
        return True, ""
