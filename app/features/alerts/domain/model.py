from pydantic import BaseModel, field_validator
from enum import Enum
from app.share.messages.domain.model import AlertType


class ParameterType(str, Enum):
    PH = "ph"
    TURBIDITY = "turbidity"
    TEMPERATURE = "temperature"
    CONDUCTIVITY = "conductivity"
    TDS = "tds"


class RangeValue(BaseModel):
    min: float
    max: float

    @field_validator('max')
    @classmethod
    def validate_max_greater_than_min(cls, v, info):
        if 'min' in info.data and v <= info.data['min']:
            raise ValueError('max debe ser mayor que min')
        return v


class AlertData(BaseModel):
    title: str
    type: AlertType
    workspace_id: str
    meter_id: str
    owner: str
    parameters: dict[ParameterType, RangeValue]

    # @field_validator('parameters')
    # @classmethod
    # def validate_all_parameters_required(cls, v):
    #     """Valida que todos los 5 parámetros estén presentes al crear"""
    #     required_params = set(ParameterType)
    #     provided_params = set(v.keys()) if v else set()

    #     if provided_params != required_params:
    #         missing = required_params - provided_params
    #         extra = provided_params - required_params

    #         error_msg = []
    #         if missing:
    #             error_msg.append(
    #                 f"Faltan parámetros requeridos: {[p.value for p in missing]}")
    #         if extra:
    #             error_msg.append(
    #                 f"Parámetros no válidos: {[p.value for p in extra]}")

    #         raise ValueError(". ".join(error_msg))

    #     return v


class Alert(AlertData):
    id: str


class AlertCreate(BaseModel):
    title: str
    type: AlertType
    workspace_id: str
    meter_id: str
    parameters: dict[ParameterType, RangeValue]

    @field_validator('parameters')
    @classmethod
    def validate_all_parameters_required(cls, v):
        """Valida que todos los 5 parámetros estén presentes al crear"""
        required_params = set(ParameterType)
        provided_params = set(v.keys()) if v else set()

        if provided_params != required_params:
            missing = required_params - provided_params
            extra = provided_params - required_params

            error_msg = []
            if missing:
                error_msg.append(
                    f"Faltan parámetros requeridos: {[p.value for p in missing]}")
            if extra:
                error_msg.append(
                    f"Parámetros no válidos: {[p.value for p in extra]}")

            raise ValueError(". ".join(error_msg))

        return v


class AlertUpdate(BaseModel):
    title: str
    type: AlertType
    parameters: dict[ParameterType, RangeValue] | None = None

    @field_validator('parameters')
    @classmethod
    def validate_parameters_keys(cls, v):
        """Valida que solo se usen claves válidas de ParameterType"""
        if v is not None:
            valid_params = set(ParameterType)
            provided_params = set(v.keys())

            invalid_params = provided_params - valid_params
            if invalid_params:
                raise ValueError(
                    f"Parámetros no válidos: {[p.value for p in invalid_params]}")

        return v


class AlertQueryParams(BaseModel):
    workspace_id: str | None = None
    meter_id: str | None = None
    type: AlertType | None = None
