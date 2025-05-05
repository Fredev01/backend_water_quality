from enum import Enum

from pydantic import BaseModel


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
    validation_count: int
    notification_count: int
    user_uid: str


class AlertActive(BaseModel):
    alert_id: str
    validation_count: int
    notification_count: int


class NotificationBody(BaseModel):
    title: str
    body: str
    user_id: str
