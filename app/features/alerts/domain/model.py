from pydantic import BaseModel, field_validator
from enum import Enum
from app.share.messages.domain.model import AlertType


class RangeValue(BaseModel):
    min: float
    max: float

    @field_validator('max')
    @classmethod
    def validate_max_greater_than_min(cls, v, info):
        if 'min' in info.data and v <= info.data['min']:
            raise ValueError('max debe ser mayor que min')
        return v


class Parameter(BaseModel):
    ph: RangeValue
    tds: RangeValue
    temperature: RangeValue
    conductivity: RangeValue
    turbidity: RangeValue


class AlertData(BaseModel):
    title: str
    type: AlertType
    workspace_id: str
    meter_id: str
    owner: str
    parameters: Parameter


class Alert(AlertData):
    id: str


class AlertCreate(BaseModel):
    title: str
    type: AlertType
    workspace_id: str
    meter_id: str
    parameters: Parameter


class AlertUpdate(BaseModel):
    title: str
    type: AlertType
    parameters: Parameter | None = None


class AlertQueryParams(BaseModel):
    workspace_id: str | None = None
    meter_id: str | None = None
    type: AlertType | None = None
