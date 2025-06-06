from pydantic import BaseModel


class VerifyResetCode(BaseModel):
    uid: str
    code: int
    exp: float
