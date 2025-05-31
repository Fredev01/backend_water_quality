from pydantic import BaseModel,  EmailStr

from app.share.users.domain.types import PhoneStr


class BaseUser(BaseModel):
    username: str
    phone: PhoneStr


class AuthBase(BaseModel):
    email: EmailStr
