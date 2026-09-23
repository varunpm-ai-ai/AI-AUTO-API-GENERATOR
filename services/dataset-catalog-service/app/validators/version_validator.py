from typing import Tuple, Dict, Any
from app.validators.base import BaseValidator


class VersionValidator(BaseValidator):
    def validate(self, payload: Dict[str, Any]) -> Tuple[bool, str]:
        checksum = payload.get("checksum")
        if not checksum or len(checksum) < 4:
            return False, "Invalid or missing checksum"
        storage_ref = payload.get("storage_ref")
        if not storage_ref:
            return False, "Missing storage_ref"
        return True, ""
