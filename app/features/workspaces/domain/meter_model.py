from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class SensorRecord(BaseModel, Generic[T]):
    id: str
    datetime: str
    value: T


class Sensor(BaseModel):
    type: str
    value: float
    list: list[SensorRecord]


class WaterQualityMeter(BaseModel):
    id: str
    name: str
    status: str
    location: str


class WaterQualityMeterSensor(BaseModel):
    sensors: list[Sensor]
