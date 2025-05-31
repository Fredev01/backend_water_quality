from app.share.response.model import ResponseApi
from app.share.users.domain.model.user import UserData


class UserLoginResponse(ResponseApi):
    user: UserData
    token: str


class UserRegisterResponse(ResponseApi):
    pass
