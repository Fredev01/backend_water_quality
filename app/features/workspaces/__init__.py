from fastapi import APIRouter, Depends, Request

from app.share.jwt.infrastructure.verify_access_token import verify_access_token


workspaces_router = APIRouter(
    prefix="/workspaces",
)


@workspaces_router.get("/")
async def get_workspaces(user=Depends(verify_access_token)):
    print(user)
    return {"message": "Get workspaces"}
