from enum import Enum

from pydantic import BaseModel


class RangeValue(BaseModel):
    min: float
    max: float


class Parameter(BaseModel):
    name: str
    range: RangeValue


class AlertType(str, Enum):
    DANGEROUS = "dangerous"
    POOR = "poor"
    MODERATE = "moderate"
    GOOD = "good"
    EXCELLENT = "excellent"


class AlertData(BaseModel):
    id: str
    title: str
    meter_id: str
    type: AlertType
    user_uid: str
    parameters: list[Parameter]


class Ranges(BaseModel):
    type: AlertType
    parameters: list[Parameter]


class NotificationControl(BaseModel):
    alert_id: str
    validation_count: int
    last_sent: float = None


class NotificationBody(BaseModel):
    id: str = None
    read: bool = False
    title: str
    body: str
    user_id: str
    timestamp: float | None = None


class NotificationBodyDatetime(BaseModel):
    id: str = None
    read: bool = False
    title: str
    body: str
    user_id: str
    datetime: str | float = None


class QueryNotificationParams(BaseModel):
    is_read: bool | None = None
    convert_timestamp: bool = False
