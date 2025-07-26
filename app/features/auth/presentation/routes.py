import time
from fastapi import APIRouter, Depends, HTTPException
from app.features.auth.domain.body import PasswordReset, ResetCode, UpdatePassword
from app.features.auth.domain.errors import AuthError
from app.features.auth.domain.response import UserLoginResponse, UserRegisterResponse
from app.features.auth.services.services import AuthService
from app.share.email.domain.errors import EmailSeedError
from app.share.email.domain.repo import EmailRepository
from app.share.email.infra.html_template import HtmlTemplate
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.access_token import AccessToken
from app.share.users.domain.errors import UserError
from app.share.users.domain.model.auth import UserLogin, UserRegister

from app.features.auth.presentation.depends import (
    get_access_token,
    get_auth_service,
    get_access_token_code,
    get_html_template,
    get_sender,
)


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login/")
async def login(
    user: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
    access_token: AccessToken = Depends(get_access_token),
) -> UserLoginResponse:

    try:

        user_login = await auth_service.login(user)

        payload = UserPayload(
            uid=user_login.uid,
            email=user_login.email,
            username=user_login.username,
            phone=user_login.phone,
            rol=user_login.rol,
            exp=time.time() + 2592000,
        ).model_dump()

        token = access_token.create(payload=payload)

        return UserLoginResponse(
            message="Logged in successfully", user=user_login, token=token
        )

    except AuthError as ae:
        raise HTTPException(status_code=ae.status_code, detail=ae.message)
    except UserError as une:
        raise HTTPException(status_code=une.status_code, detail=une.message)
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@auth_router.post("/register/")
async def register(
    user: UserRegister,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRegisterResponse:

    try:
        await auth_service.register(user)
        return UserRegisterResponse(message="Registered successfully")
    except UserError as ue:
        raise HTTPException(status_code=ue.status_code, detail=ue.message)
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail="Data error")
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@auth_router.post("/request-password-reset/")
async def request_password_reset(
    password_reset: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service),
    html_template: HtmlTemplate = Depends(get_html_template),
    sender: EmailRepository = Depends(get_sender),
):
    try:
        generate_code = await auth_service.generate_verification_code(
            password_reset.email
        )

        body = html_template.get_reset_password(
            generate_code.username, generate_code.code
        )

        sender.send(
            to=password_reset.email,
            subject="Reset password",
            body=body,
            raise_error=True,
        )

        return {"message": "Código de verificación enviado"}
    except EmailSeedError as ese:
        raise HTTPException(status_code=ese.status_code, detail=ese.message)
    except UserError as une:
        raise HTTPException(status_code=une.status_code, detail=une.message)
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@auth_router.post("/verify-reset-code/")
async def verify_reset_code(
    reset_code: ResetCode,
    auth_service: AuthService = Depends(get_auth_service),
    access_token_code: AccessToken = Depends(get_access_token_code),
):
    try:
        verify = await auth_service.verify_reset_code(reset_code.email, reset_code.code)

        token = access_token_code.create(payload=verify.model_dump())
        return {"message": "Código de verificación válido", "token": token}
    except AuthError as ae:
        raise HTTPException(status_code=ae.status_code, detail=ae.message)
    except UserError as ue:
        raise HTTPException(status_code=ue.status_code, detail=ue.message)
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@auth_router.post("/reset-password/")
async def reset_password(
    token: str,
    update_password: UpdatePassword,
    auth_service: AuthService = Depends(get_auth_service),
    access_token_code: AccessToken = Depends(get_access_token_code),
):

    try:
        payload = access_token_code.validate(token)
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=401, detail="Token inválido")

    uid = payload["uid"]

    try:
        await auth_service.get_verification_code(uid=uid, code=payload["code"])

        user_data = await auth_service.change_password(
            uid=uid, new_password=update_password.new_password
        )

        return {"message": "Contraseña actualizada con éxito", "user": user_data}
    except AuthError as ae:
        raise HTTPException(status_code=ae.status_code, detail=ae.message)
    except UserError as ue:
        raise HTTPException(status_code=ue.status_code, detail=ue.message)
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
