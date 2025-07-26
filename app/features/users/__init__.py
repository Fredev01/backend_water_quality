from fastapi import APIRouter, Depends
from app.features.users.domian.response import UserResponse, UsersResponse
from app.share.depends import get_user_repo
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.verify_access_token import (
    verify_access_admin_token,
    verify_access_token,
)
from app.share.users.domain.model.user import UserUpdate
from app.share.users.domain.repository import UserRepository

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/")
async def get_users(
    page_token: str = None,
    user=Depends(verify_access_admin_token),
    user_repo: UserRepository = Depends(get_user_repo),
) -> UsersResponse:
    return UsersResponse(
        message="Get users successfully.",
        users=user_repo.get_all(page_token=page_token),
    )


@users_router.get("/me")
async def get_me(
    user: UserPayload = Depends(verify_access_token),
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserResponse:
    userdata = user_repo.get_by_uid(user.uid)

    return UserResponse(message="Get user successfully.", user=userdata)


@users_router.put("/me")
async def update_me(
    user: UserUpdate,
    user_payload: UserPayload = Depends(verify_access_token),
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserResponse:
    userdata = user_repo.update_user(user_payload.uid, user)

    return UserResponse(message="User updated successfully.", user=userdata)
