from fastapi import APIRouter, HTTPException
from app.features.auth.domain.model import UserLogin, UserRegister
from app.features.auth.infrastructure.access_token import AccessToken
from app.features.auth.services.services import AuthService
from firebase_admin.auth import UserNotFoundError

auth_router = APIRouter(
    prefix="/auth",
)

auth_service = AuthService()
access_token = AccessToken()


@auth_router.post("/login/")
async def login(user: UserLogin):
    try:

        user_login = auth_service.login(user)

        token = access_token.create(user_login)

        return {"message": "Logged in successfully", "user": user_login, "token": token}
    except UserNotFoundError:
        raise HTTPException(status_code=401, detail="Unregistered user")
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
        raise HTTPException(status_code=400, detail="ve")
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
