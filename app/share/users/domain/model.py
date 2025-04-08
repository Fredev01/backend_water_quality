from pydantic import BaseModel


class UserDetail(BaseModel):
    uid: str
    username: str
    email: str
    phone: str
