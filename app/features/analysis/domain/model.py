from datetime import datetime, date
from typing import Any, ClassVar

from pydantic import BaseModel

from app.features.analysis.domain.enums import CorrMethodEnum, PeriodEnum
from app.features.analysis.domain.types import AheadPrediction
from app.share.meter_records.domain.enums import SensorType
from app.share.meter_records.domain.model import SensorQueryParams, SensorIdentifier


class Period(BaseModel):
    start_date: datetime
    end_date: datetime


class AverageStats(BaseModel):
    average: float
    min: float
    max: float


class AverageResult(BaseModel):
    sensor: str
    period: Period
    stats: AverageStats


class AvgResult(BaseModel):
    date: datetime
    value: float | None


class AvgPeriodResult(BaseModel):
    sensor: str
    period: Period
    period_type: PeriodEnum
    averages: list[AvgResult]


class AvgSensor(BaseModel):
    conductivity: float | None
    ph: float | None
    temperature: float | None
    tds: float | None
    turbidity: float | None


class AvgPeriod(BaseModel):
    date: datetime
    averages: AvgSensor


class AvgPeriodAllResult(BaseModel):
    period: Period
    period_type: PeriodEnum
    averages: list[AvgPeriod]


class AverageRange(SensorQueryParams):
    limit: ClassVar[int] = None
    index: ClassVar[str] = None
    ignore_limit: ClassVar[bool] = None


class AveragePeriod(AverageRange):
    period_type: PeriodEnum = PeriodEnum.DAYS


class PredictionParam(AveragePeriod):
    ahead: AheadPrediction = 10


class PredictionData(BaseModel):
    labels: list[str]
    conductivity: list[float | None]
    ph: list[float | None]
    temperature: list[float | None]
    tds: list[float | None]
    turbidity: list[float | None]


class PredictionResultAll(BaseModel):
    data: PredictionData
    pred: PredictionData


class PredData(BaseModel):
    labels: list[str]
    values: list[float | None]


class PredictionResult(BaseModel):
    sensor: SensorType
    data: PredData
    pred: PredData


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
