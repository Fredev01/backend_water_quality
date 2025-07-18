from pydantic import BaseModel, EmailStr

from app.share.users.domain.types import PasswordStr


class UpdatePassword(BaseModel):
    new_password: PasswordStr


class PasswordReset(BaseModel):
    email: EmailStr


class ResetCode(BaseModel):
    email: EmailStr
    code: int
