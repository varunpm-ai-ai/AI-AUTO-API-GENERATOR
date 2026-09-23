from typing import Tuple, Dict, Any, List
from app.validators.factory import ValidationFactory
from app.logger import logger


class ValidationManager:
    def validate(self, payload: Dict[str, Any], validator_types: List[str]) -> Tuple[bool, str]:
        for v_type in validator_types:
            try:
                validator = ValidationFactory.get_validator(v_type)
                is_valid, err = validator.validate(payload)
                if not is_valid:
                    logger.warning(f"Validation failed for '{v_type}': {err}")
                    return False, f"[{v_type.upper()}] {err}"
            except Exception as e:
                logger.error(f"Validation error running '{v_type}': {e}")
                return False, str(e)
        return True, ""


validation_manager = ValidationManager()
