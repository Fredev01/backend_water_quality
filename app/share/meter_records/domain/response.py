from pydantic import BaseModel
from app.share.socketio.domain.model import Record, SRColorValue


class SensorRecordsResponse(BaseModel):
    color: list[Record[SRColorValue]]
    conductivity: list[Record[float]]
    ph: list[Record[float]]
    temperature: list[Record[float]]
    tds: list[Record[float]]
    turbidity: list[Record[float]]
