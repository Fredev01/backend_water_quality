from typing import ClassVar
from pydantic import BaseModel

from app.share.meter_records.domain.model import SensorQueryParams, SensorIdentifier


class AvarageRange(SensorQueryParams):
    limit: ClassVar[int] = None
    index: ClassVar[str] = None


class AvarageIdentifier(SensorIdentifier):
    sensor_name: ClassVar[str] = None
    user_id: ClassVar[str] = None


class AvarageModel(BaseModel):
    workspace_id: str
    meter_id: str
    query_params: AvarageRange
