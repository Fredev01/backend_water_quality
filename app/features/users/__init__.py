from fastapi import APIRouter, Depends
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.share.users.domain.model.user import UserDetail, UserUpdate
from app.share.users.infra.users_repo_impl import UserRepositoryImpl

users_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

user_repo = UserRepositoryImpl()


@users_router.get("/")
async def get_users(user=Depends(verify_access_token)):

    return {"message": "List of users will be here."}


@users_router.get("/me")
async def get_me(user: UserPayload = Depends(verify_access_token)):
    user_detail = user_repo.get_by_uid(user.uid)

    return {"message": "My user.", "user": user_detail}


@users_router.put("/me")
async def update_me(user: UserUpdate, user_payload: UserPayload = Depends(verify_access_token)):
    user_detail = user_repo.update_user(user_payload.uid, user)
    return {"message": "User updated successfully.", "user": user_detail}
