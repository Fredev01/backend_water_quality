from fastapi import APIRouter
from app.features.auth.domain.model import UserLogin, UserRegister
from app.features.auth.services.services import AuthService

auth_router = APIRouter(
    prefix="/auth",
)

auth_service = AuthService()


@auth_router.post("/login/")
async def login(user: UserLogin):

    login_user = auth_service.login(user)

    print(
        login_user.uid,
        login_user.email,
        login_user.display_name,
    )
    return {"message": "Logged in successfully"}


@auth_router.post("/register/")
async def register(user: UserRegister):

    new_user = auth_service.register(user)

    print(new_user)

    return {"message": "Registered successfully"}
