from pydantic import BaseModel, EmailStr
from app.share.users.domain.model.base import AuthBase, BaseUser
from app.share.users.domain.types import PasswordStr, PhoneStr


class UserData(BaseUser):
    uid: str | None = None
    rol: str


class UserDetail(BaseUser, AuthBase):
    uid: str


class UserUpdate(BaseModel):
    username: str | None = None
    phone: PhoneStr | None = None
    email: EmailStr | None = None
    password: PasswordStr | None = None
