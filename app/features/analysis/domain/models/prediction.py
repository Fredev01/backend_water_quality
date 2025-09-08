from pydantic import BaseModel

from app.features.analysis.domain.models.average import AveragePeriod
from app.features.analysis.domain.types import AheadPrediction
from app.share.meter_records.domain.enums import SensorType


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
