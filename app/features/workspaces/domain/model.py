from pydantic import BaseModel, ValidationError, field_validator


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


class WorkspaceConnectionPayload(BaseModel):
    id_workspace: str
    id_meter: str
    exp: float
