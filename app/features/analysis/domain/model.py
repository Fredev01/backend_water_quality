from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel

from app.features.analysis.domain.enums import CorrMethodEnum, PeriodEnum
from app.features.analysis.domain.types import AheadPrediction
from app.share.meter_records.domain.enums import SensorType
from app.share.meter_records.domain.model import SensorQueryParams, SensorIdentifier
from app.share.socketio.domain.model import Record, SRColorValue


class Chart(BaseModel):
    type: str
    title: str
    labels: list[str]
    values: list


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
    charts: list[Chart]


class AvgResult(BaseModel):
    date: datetime
    value: float | None


class AvgPeriodResult(BaseModel):
    sensor: str
    period: Period
    period_type: PeriodEnum
    averages: list[AvgResult]
    charts: list[Chart]


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
    charts: list[Chart]


class AverageRange(SensorQueryParams):
    limit: ClassVar[int] = None
    index: ClassVar[str] = None
    ignore_limit: ClassVar[bool] = None


class AveragePeriod(AverageRange):
    period_type: PeriodEnum = PeriodEnum.DAYS


class PredictionParam(AveragePeriod):
    ahead: AheadPrediction = 10


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
    chart: Chart
