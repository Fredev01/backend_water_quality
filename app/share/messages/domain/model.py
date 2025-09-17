from enum import Enum

from pydantic import BaseModel

from app.share.parameters.domain.model import Parameter


class AlertType(str, Enum):
    DANGEROUS = "dangerous"
    POOR = "poor"
    MODERATE = "moderate"
    GOOD = "good"
    EXCELLENT = "excellent"


class ResultValidationAlert(BaseModel):
    alerts_ids: list[str] = []
    has_parameters: bool = False


class PriorityParameters(list[str], Enum):
    parameters: list[str] = ["ph", "turbidity"]


class AlertData(BaseModel):
    id: str
    title: str
    meter_id: str
    type: AlertType
    user_uid: str
    parameters: Parameter | None = None


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
