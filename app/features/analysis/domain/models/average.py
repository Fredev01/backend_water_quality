from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel

from app.features.analysis.domain.enums import PeriodEnum
from app.share.meter_records.domain.model import SensorQueryParams


class Period(BaseModel):
    start_date: datetime
    end_date: datetime


class AverageStats(BaseModel):
    average: float
    min: float
    max: float


class AverageStatsSensor(AverageStats):
    sensor: str


class AverageResult(BaseModel):
    sensor: str
    period: Period
    stats: AverageStats


class AverageResultAll(BaseModel):
    period: Period
    result: list[AverageStatsSensor]


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


class AvgPeriodParam(AverageRange):
    period_type: PeriodEnum = PeriodEnum.DAYS
