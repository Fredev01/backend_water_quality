from pydantic import BaseModel


class User(BaseModel):
    email: str
    password: str


class UserLogin(User):
    pass


class UserRegister(User):
    username: str
    phone: str | int


class UserPayload(UserRegister):
    rol: str


class TokenPayload(BaseModel):
    access_token: str
    token_type: str
    payload: UserPayload
