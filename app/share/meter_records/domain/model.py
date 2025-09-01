from pydantic import BaseModel
from datetime import datetime


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
    sensor_type: str | None = None


class Chart(BaseModel):
    type: str
    labels: list[datetime]
    values: list[float]


class Period(BaseModel):
    start_date: datetime
    end_date: datetime


class Stats(BaseModel):
    average: float
    min: float
    max: float
    out_of_range_percent: float


class AvarageResult(BaseModel):
    sensor: str
    period: Period
    stats: Stats
    chart: Chart
