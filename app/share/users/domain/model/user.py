from pydantic import BaseModel, EmailStr
from app.share.users.domain.enum.roles import Roles
from app.share.users.domain.model.base import AuthBase, BaseUser
from app.share.users.domain.types import PasswordStr, PhoneStr


class UserData(BaseUser, AuthBase):
    uid: str | None = None
    rol: Roles | None = None


class UserDetail(BaseUser, AuthBase):
    uid: str


class UserUpdate(BaseModel):
    username: str | None = None
    phone: PhoneStr | None = None
    email: EmailStr | None = None
    password: PasswordStr | None = None
