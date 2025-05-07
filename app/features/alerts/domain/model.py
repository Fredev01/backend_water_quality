from pydantic import BaseModel
from app.share.messages.domain.model import AlertType


class AlertData(BaseModel):
    title: str
    type: AlertType
    workspace_id: str
    meter_id: str
    owner: str


class Alert(AlertData):
    id: str


class AlertCreate(BaseModel):
    title: str
    type: AlertType
    workspace_id: str
    meter_id: str


class AlertUpdate(BaseModel):
    title: str
    type: AlertType


class AlertQueryParams(BaseModel):
    workspace_id: str | None = None
    meter_id: str | None = None
    type: AlertType | None = None
