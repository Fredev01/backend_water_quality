from pydantic import BaseModel, ValidationError, field_validator

class Workspace(BaseModel):
    name: str
    owner: str

class WorkspaceCreate(BaseModel):
    name: str
    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str):
        if len(value) < 3:
            raise ValueError(
                "El nombre del workspace debe tener al menos 3 caracteres.")
        return value

class WorkspaceResponse(Workspace):
    id: str