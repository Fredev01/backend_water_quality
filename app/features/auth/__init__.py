from fastapi import APIRouter
from app.features.auth.domain.model import UserLogin, UserRegister

auth_router = APIRouter(
    prefix="/auth",
)


@auth_router.post("/login/")
async def login(user: UserLogin):
    print(
        user.email,
        user.password,
    )
    return {"message": "Logged in successfully"}


@auth_router.post("/register/")
async def register(user: UserRegister):
    print(
        user.email,
        user.password,
    )
    return {"message": "Registered successfully"}
