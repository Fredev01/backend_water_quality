from enum import Enum

from pydantic import BaseModel


class AlertType(str, Enum):
    DANGEROUS = "dangerous"
    POOR = "poor"
    MODERATE = "moderate"
    GOOD = "good"
    EXCELLENT = "excellent"


class Alert(BaseModel):
    id: str
    title: str
    meter_id: str
    type: AlertType
    validation_count: int
    notification_count: int
    user_uid: str


class AlertValidated(BaseModel):
    id: str
    meter_id: str
    title: str
    type: AlertType
    user_uid: str
