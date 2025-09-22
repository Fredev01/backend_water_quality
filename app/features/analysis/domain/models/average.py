from datetime import datetime
from pydantic import BaseModel

from app.features.analysis.domain.enums import PeriodEnum
from app.share.meter_records.domain.enums import SensorType


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


class AvgValues(BaseModel):
    labels: list[datetime]
    values: list[float | None]


class AvgSensor(BaseModel):
    conductivity: AvgValues
    ph: AvgValues
    temperature: AvgValues
    tds: AvgValues
    turbidity: AvgValues


class AvgPeriodAllResult(BaseModel):
    period: Period
    period_type: PeriodEnum
    results: AvgSensor


class AverageRange(BaseModel):
    start_date: str
    end_date: str
    sensor_type: SensorType | None = None


class AvgPeriodParam(AverageRange):
    period_type: PeriodEnum = PeriodEnum.DAYS
