from typing import Tuple, Dict, Any
from app.validators.base import BaseValidator


class IdentityValidator(BaseValidator):
    def validate(self, payload: Dict[str, Any]) -> Tuple[bool, str]:
        name = payload.get("name") or payload.get("dataset_name")
        source = payload.get("source")
        domain = payload.get("domain")

        if not name or not name.strip():
            return False, "Dataset name is required"
        if not source or not source.strip():
            return False, "Source is required"
        if not domain or not domain.strip():
            return False, "Domain is required"

        return True, ""
