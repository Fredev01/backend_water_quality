from pydantic import BaseModel


class ResponseApi(BaseModel):
    message: str
