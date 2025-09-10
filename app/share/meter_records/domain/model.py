from pydantic import BaseModel

from app.share.meter_records.domain.enums import SensorType
from app.share.socketio.domain.model import Record, SRColorValue


class SensorIdentifier(BaseModel):
    workspace_id: str
    meter_id: str
    user_id: str
    sensor_name: str | None = None


class SensorQueryParams(BaseModel):
    limit: int = 10
    ignore_limit: bool = False
    index: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    sensor_type: SensorType | None = None


class RecordEntry(BaseModel):
    color: Record[SRColorValue] | None = None
    conductivity: Record[float] | None = None
    ph: Record[float] | None = None
    temperature: Record[float] | None = None
    tds: Record[float] | None = None
    turbidity: Record[float] | None = None


type RecordsDict = dict[str, RecordEntry]
