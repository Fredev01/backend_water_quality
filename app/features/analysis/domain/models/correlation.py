from typing import ClassVar
from pydantic import BaseModel

from app.features.analysis.domain.enums import CorrMethodEnum
from app.features.analysis.domain.models.average import AveragePeriod
from app.share.meter_records.domain.enums import SensorType
from app.share.meter_records.domain.model import SensorIdentifier


class CorrelationParams(AveragePeriod):
    sensor_type: ClassVar[SensorType] = None
    sensors: list[SensorType]
    method: CorrMethodEnum = CorrMethodEnum.PEARSON


class AverageIdentifier(SensorIdentifier):
    sensor_name: ClassVar[str] = None
    user_id: ClassVar[str] = None


class CorrelationResult(BaseModel):
    method: str
    sensors: list | None
    matrix: list | None
