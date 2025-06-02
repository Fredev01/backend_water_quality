from fastapi import APIRouter, Depends, HTTPException
from app.features.users.domian.response import UserResponse,  UsersResponse
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.verify_access_token import verify_access_admin_token, verify_access_token
from app.share.users.domain.enum.roles import Roles
from app.share.users.domain.model.user import UserDetail, UserUpdate
from app.share.users.infra.users_repo_impl import UserRepositoryImpl

users_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

user_repo = UserRepositoryImpl()


@users_router.get("/")
async def get_users(page_token: str = None, user=Depends(verify_access_admin_token)) -> UsersResponse:
    return UsersResponse(message="Get users successfully.", users=user_repo.get_all(page_token=page_token))


@users_router.get("/me")
async def get_me(user: UserPayload = Depends(verify_access_token)) -> UserResponse:
    userdata = user_repo.get_by_uid(user.uid)

    return UserResponse(message="Get user successfully.", user=userdata)


@users_router.put("/me")
async def update_me(user: UserUpdate, user_payload: UserPayload = Depends(verify_access_token)) -> UserResponse:
    userdata = user_repo.update_user(user_payload.uid, user)

    return UserResponse(message="User updated successfully.", user=userdata)
