from pydantic import BaseModel, field_validator

from app.share.users.domain.model.user import UserData
from app.share.workspace.domain.model import (
    WorkspaceRoles,
    WorkspaceRolesAll,
    WorkspaceType,
)


class Workspace(BaseModel):
    name: str
    owner: str | None
    type: WorkspaceType = WorkspaceType.PRIVATE


class WorkspaceCreate(BaseModel):
    name: str
    type: WorkspaceType = WorkspaceType.PRIVATE

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        if len(value.strip()) < 3:
            raise ValueError(
                "El nombre del workspace debe tener al menos 3 caracteres."
            )
        if len(value.strip()) > 50:
            raise ValueError(
                "El nombre del workspace no puede tener más de 50 caracteres."
            )
        return value


class WorkspaceResponse(Workspace):
    id: str
    user: UserData | None = None
    rol: WorkspaceRoles | WorkspaceRolesAll = WorkspaceRolesAll.UNKNOWN


class WorkspaceShareResponse(WorkspaceResponse):
    guest: str


class GuestResponse(BaseModel):
    uid: str
    email: str
    username: str
    rol: WorkspaceRoles


class WorkspacePublicResponse(BaseModel):
    id: str
    name: str


class WorkspaceGuestCreate(BaseModel):
    guest: str
    rol: WorkspaceRoles


class WorkspaceGuestUpdate(BaseModel):
    rol: WorkspaceRoles


class WorkspaceGuestDelete(BaseModel):
    workspace_id: str
    user: str
    guest: str


class WorkspaceConnectionPayload(BaseModel):
    id_workspace: str
    id_meter: str
    exp: float
