from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class SRColorValue(BaseModel):
    r: int
    g: int
    b: int


class RecordBody(BaseModel):
    color: SRColorValue
    conductivity: float
    ph: float
    temperature: float
    tds: float
    turbidity: float


class Record(BaseModel, Generic[T]):
    id: str = None
    value: T
    datetime: str


class RecordResponse(BaseModel):
    color: Record[SRColorValue]
    conductivity: Record[float]
    ph: Record[float]
    temperature: Record[float]
    tds: Record[float]
    turbidity: Record[float]
