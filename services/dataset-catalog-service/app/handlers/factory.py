from app.constants import RegistrationType
from app.handlers.base import BaseRegistrationHandler
from app.handlers.new_dataset_handler import NewDatasetHandler
from app.handlers.existing_dataset_handler import ExistingDatasetHandler
from app.handlers.re_registration_handler import ReRegistrationHandler


class RegistrationFactory:
    @staticmethod
    def get_handler(reg_type: RegistrationType) -> BaseRegistrationHandler:
        if reg_type == RegistrationType.NEW:
            return NewDatasetHandler()
        elif reg_type == RegistrationType.EXISTING:
            return ExistingDatasetHandler()
        elif reg_type == RegistrationType.RE_REGISTRATION:
            return ReRegistrationHandler()
        else:
            raise ValueError(f"Unsupported registration type: {reg_type}")
