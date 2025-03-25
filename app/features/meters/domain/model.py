from enum import Enum
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class Location(BaseModel):
    lat: float
    lon: float


class SensorStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class SensorRecord(BaseModel, Generic[T]):
    id: str
    datetime: str
    value: T


class Sensor(BaseModel):
    type: str
    value: float
    list: list[SensorRecord]


class WQMeterCreate(BaseModel):
    name: str
    location: Location


class WQMeter(WQMeterCreate):
    status: SensorStatus = SensorStatus.DISABLED


class WaterQualityMeter(WQMeter):
    id: str


class WaterQMSensorPayload(BaseModel):
    id_workspace: str
    owner: str


class WaterQualityMeterSensor(BaseModel):
    sensors: list[Sensor]


class MeterConnection(BaseModel):
    id: str
    id_workspace: str
    owner: str
    id_meter: str
