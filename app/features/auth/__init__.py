import time
from fastapi import APIRouter, HTTPException
from app.features.auth.domain.body import UpdatePassword
from app.features.auth.domain.model import VerifyResetCode
from app.features.auth.domain.response import UserLoginResponse, UserRegisterResponse
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.access_token import AccessToken
from app.features.auth.services.services import AuthService
from app.share.users.domain.model.auth import UserLogin, UserRegister
from app.share.users.infra.users_repo_impl import UserRepositoryImpl

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

auth_service = AuthService(user_repo=UserRepositoryImpl())
access_token = AccessToken[UserPayload]()
access_token_code = AccessToken[VerifyResetCode]()


@auth_router.post("/login/")
async def login(user: UserLogin) -> UserLoginResponse:
    try:

        user_login = await auth_service.login(user)

        payload = UserPayload(
            uid=user_login.uid,
            email=user_login.email,
            username=user_login.username,
            phone=user_login.phone,
            rol=user_login.rol,
            exp=time.time() + 2592000
        ).model_dump()

        token = access_token.create(payload=payload)

        return UserLoginResponse(
            message="Logged in successfully",
            user=user_login,
            token=token
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@auth_router.post("/register/")
async def register(user: UserRegister) -> UserRegisterResponse:

    try:
        new_user = await auth_service.register(user)
        return UserRegisterResponse(message="Registered successfully")
    except HTTPException as he:
        raise he
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail="Data error")
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@auth_router.post("/request-password-reset/")
async def request_password_reset(email: str):
    code = await auth_service.generate_verification_code(email)

    print(code)
    return {"message": "Código de verificación enviado"}


@auth_router.post("/verify-reset-code/")
async def verify_reset_code(email: str, code: int):
    verify = await auth_service.verify_reset_code(email, code)
    print(verify)
    if not verify:
        raise HTTPException(status_code=400, detail="Invalid code")

    token = access_token_code.create(payload=verify.model_dump())
    return {"message": "Código de verificación válido", "token": token}


@auth_router.post("/reset-password/")
async def reset_password(token: str, update_password: UpdatePassword):

    try:
        payload = access_token_code.validate(token)
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=401, detail="Token inválido")

    uid = payload["uid"]

    is_valid = await auth_service.get_verification_code(uid=uid, code=payload["code"])

    if not is_valid:
        raise HTTPException(
            status_code=400, detail="Código de verificación inválido")

    user_data = await auth_service.change_password(uid=uid, new_password=update_password.new_password)

    return {"message": "Contraseña actualizada con éxito", "user": user_data}
