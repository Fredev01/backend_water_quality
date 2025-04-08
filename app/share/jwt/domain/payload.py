from pydantic import BaseModel


class UserPayload(BaseModel):
    uid: str
    email: str
    username: str
    phone: str
    rol: str
    exp: float


class MeterPayload(BaseModel):
    id_workspace: str
    owner: str
    id_meter: str
