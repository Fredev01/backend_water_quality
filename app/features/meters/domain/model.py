from enum import Enum
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from app.share.socketio.domain.model import Record, SRColorValue


T = TypeVar("T")


class SensorRecord(BaseModel, Generic[T]):
    id: str
    datetime: str
    value: T


class Sensor(BaseModel):
    type: str
    list: list[SensorRecord]


class Location(BaseModel):
    lat: float
    lon: float


class SensorStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class WQMeterCreate(BaseModel):
    name: str
    location: Location


class WQMeterUpdate(WQMeterCreate):
    pass


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

class SensorRecordsResponse(BaseModel):
    color: list[Record[SRColorValue]]
    conductivity: list[Record[float]]
    ph: list[Record[float]]
    temperature: list[Record[float]]
    tds: list[Record[float]]
    turbidity: list[Record[float]]

class SensorQueryParams(BaseModel):
    limit: int = 10
    descending: bool = True
    convert_timestamp: bool = False
    
class SensorIdentifier(BaseModel):
    workspace_id: str
    meter_id: str
    user_id: str
    sensor_name: Optional[str] = None
class RecordDatetime(BaseModel, Generic[T]):
    value: T
    datetime: str