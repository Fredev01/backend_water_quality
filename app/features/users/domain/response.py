from app.share.response.model import ResponseApi
from app.share.users.domain.model.user import UserData


class UsersResponse(ResponseApi):
    users: list[UserData]


class UserResponse(ResponseApi):
    user: UserData
