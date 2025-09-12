from pydantic import BaseModel
from app.share.messages.domain.model import AlertType


class RangeValue(BaseModel):
    min: float
    max: float


class Parameter(BaseModel):
    name: str
    range: RangeValue


class AlertData(BaseModel):
    title: str
    type: AlertType
    workspace_id: str
    meter_id: str
    owner: str
    parameters: dict[str, Parameter]


class Alert(AlertData):
    id: str


class AlertCreate(BaseModel):
    title: str
    type: AlertType
    workspace_id: str
    meter_id: str
    parameters: list[Parameter]


class AlertUpdate(BaseModel):
    title: str
    type: AlertType
    parameters: dict[str, Parameter] | None = None


class AlertQueryParams(BaseModel):
    workspace_id: str | None = None
    meter_id: str | None = None
    type: AlertType | None = None
