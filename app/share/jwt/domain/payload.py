from pydantic import BaseModel


class UserPayload(BaseModel):
    uid: str
    email: str
    username: str
    phone: str | None = None
    rol: str
    exp: float


class MeterPayload(BaseModel):
    id_workspace: str
    owner: str
    id_meter: str
