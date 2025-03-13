from app.features.auth.domain.model import UserData
from app.share.response.model import ResponseApi


class UserLoginResponse(ResponseApi):
    user: UserData
    token: str


class UserRegisterResponse(ResponseApi):
    pass
