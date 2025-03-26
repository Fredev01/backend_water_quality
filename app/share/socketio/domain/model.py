from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class SRColorValue(BaseModel):
    r: int
    g: int
    b: int


class RecordBody(BaseModel, Generic[T]):
    color: SRColorValue
    conductivity: float
    ph: float
    temperature: float
    tds: float
    turbidity: float
