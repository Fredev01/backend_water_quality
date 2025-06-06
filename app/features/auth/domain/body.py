from pydantic import BaseModel

from app.share.users.domain.types import PasswordStr


class UpdatePassword(BaseModel):
    new_password: PasswordStr
