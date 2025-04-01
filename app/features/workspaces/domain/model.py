from pydantic import BaseModel,  field_validator
from enum import Enum


class WorkspaceRoles(str, Enum):
    VISITOR = "visitor"
    MANAGER = "manager"
    ADMINISTRATOR = "administrator"


class Workspace(BaseModel):
    name: str
    owner: str


class WorkspaceCreate(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str):
        if len(value.strip()) < 3:
            raise ValueError(
                "El nombre del workspace debe tener al menos 3 caracteres.")
        if len(value.strip()) > 50:
            raise ValueError(
                "El nombre del workspace no puede tener más de 50 caracteres.")
        return value


class WorkspaceResponse(Workspace):
    id: str


class WorkspaceShareResponse(WorkspaceResponse):
    guest: str
    rol: WorkspaceRoles


class GuestResponse(BaseModel):
    id: str
    email: str
    rol: WorkspaceRoles


class WorkspacePublicResponse(BaseModel):
    id: str
    name: str


class WorkspaceShareCreate(BaseModel):
    guest: str
    rol: WorkspaceRoles


class WorkspaceShareUpdate(WorkspaceShareCreate):
    id: str


class WorkspaceShareDelete(BaseModel):
    id: str
    workspace_id: str
    owner: str
    guest: str


class WorkspaceConnectionPayload(BaseModel):
    id_workspace: str
    id_meter: str
    exp: float
