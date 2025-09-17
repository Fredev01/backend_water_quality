from pydantic import BaseModel
from app.share.messages.domain.model import AlertType
from app.share.parameters.domain.model import Parameter


class AlertData(BaseModel):
    title: str
    type: AlertType
    workspace_id: str
    meter_id: str
    owner: str
    parameters: Parameter | None


class Alert(AlertData):
    id: str


class AlertCreate(BaseModel):
    title: str
    type: AlertType
    workspace_id: str
    meter_id: str
    parameters: Parameter


class AlertUpdate(BaseModel):
    title: str
    type: AlertType
    parameters: Parameter | None = None


class AlertQueryParams(BaseModel):
    workspace_id: str | None = None
    meter_id: str | None = None
    type: AlertType | None = None
