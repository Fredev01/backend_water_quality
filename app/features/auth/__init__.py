from fastapi import APIRouter, HTTPException
from app.features.auth.domain.model import UserLogin, UserRegister
from app.features.auth.services.services import AuthService
from firebase_admin.auth import UserNotFoundError

auth_router = APIRouter(
    prefix="/auth",
)

auth_service = AuthService()


@auth_router.post("/login/")
async def login(user: UserLogin):
    try:

        login_user = auth_service.login(user)

        print(
            login_user.uid,
            login_user.email,
            login_user.display_name,
        )
        return {"message": "Logged in successfully"}
    except UserNotFoundError:
        raise HTTPException(status_code=401, detail="Unregistered user")
    except HTTPException as he:
        raise he
    except Exception as e:
        print(e.__class__.__name__)
        raise HTTPException(status_code=500, detail="Server error")


@auth_router.post("/register/")
async def register(user: UserRegister):

    new_user = auth_service.register(user)

    print(new_user)

    return {"message": "Registered successfully"}
