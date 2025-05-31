from app.share.users.domain.model.base import AuthBase, BaseUser
from app.share.users.domain.types import PasswordStr


class UserLogin(AuthBase):
    password: PasswordStr


class UserRegister(BaseUser, AuthBase):
    password: PasswordStr
