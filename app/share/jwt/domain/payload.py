from pydantic import BaseModel


class UserPayload(BaseModel):

    email: str
    username: str
    phone: str
    rol: str
    exp: float
