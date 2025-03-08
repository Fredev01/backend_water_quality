import time
from fastapi import APIRouter, HTTPException
from app.features.auth.domain.model import UserLogin, UserRegister
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.access_token import AccessToken
from app.features.auth.services.services import AuthService

auth_router = APIRouter(
    prefix="/auth",
)

auth_service = AuthService()
access_token = AccessToken[UserPayload]()


@auth_router.post("/login/")
async def login(user: UserLogin):
    try:

        user_login = auth_service.login(user)

        payload = UserPayload(
            email=user_login.email,
            username=user_login.username,
            phone=user_login.phone,
            rol=user_login.rol,
            exp=time.time() + 2592000
        ).model_dump()

        token = access_token.create(payload=payload)

        return {"message": "Logged in successfully", "user": user_login, "token": token}

    except HTTPException as he:
        raise he
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@auth_router.post("/register/")
async def register(user: UserRegister):

    try:
        print(user)
        new_user = auth_service.register(user)
        print(new_user)
        auth_service.save_userData(new_user, "client")
        print("new user")
        return {"message": "Registered successfully"}
    except HTTPException as he:
        raise he
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail="Data error")
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
