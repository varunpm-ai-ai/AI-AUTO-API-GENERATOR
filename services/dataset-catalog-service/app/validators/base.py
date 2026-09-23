from abc import ABC, abstractmethod
from typing import Tuple, Any, Dict


class BaseValidator(ABC):
    @abstractmethod
    def validate(self, payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates payload.
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        pass
