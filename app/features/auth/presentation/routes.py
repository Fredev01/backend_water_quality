import time
import random
from datetime import datetime, timedelta
import urllib.parse
import httpx
import os
import secrets

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from app.features.auth.domain.body import PasswordReset, ResetCode, UpdatePassword
from app.features.auth.domain.errors import AuthError
from app.features.auth.domain.response import UserLoginResponse, UserRegisterResponse
from app.features.auth.services.services import AuthService
from app.share.email.domain.errors import EmailSeedError
from app.share.email.domain.repo import EmailRepository
from app.share.email.infra.html_template import HtmlTemplate
from app.share.email.presentation.depends import get_html_template, get_sender
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.access_token import AccessToken
from app.share.users.domain.errors import UserError
from app.share.users.domain.model.auth import UserLogin, UserRegister
from app.share.oauth.domain.config import GithubOAuthConfigImpl

from app.features.auth.presentation.depends import (
    get_access_token,
    get_auth_service,
    get_access_token_code,
)

config = GithubOAuthConfigImpl()
GITHUB_CLIENT_ID = config.client_id
GITHUB_CLIENT_SECRET = config.client_secret
GITHUB_CALLBACK_URL = config.callback_url
FRONTEND_ORIGIN = config.frontend_origin

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
    except UserError as ue:
        raise HTTPException(status_code=ue.status_code, detail=ue.message)
    except Exception as e:
        print(e.__class__.__name__, e)
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
        print(e.__class__.__name__, e)
        raise HTTPException(status_code=500, detail="Server error")

@auth_router.post("/request-password-reset/")
async def request_password_reset(
    password_reset: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service),
    html_template: HtmlTemplate = Depends(get_html_template),
    sender: EmailRepository = Depends(get_sender),
):
    try:
        generate_code = await auth_service.generate_verification_code(password_reset.email)
        body = html_template.get_reset_password(generate_code.username, generate_code.code)
        sender.send(to=password_reset.email, subject="Reset password", body=body, raise_error=True)
        return {"message": "Código de verificación enviado"}
    except EmailSeedError as ese:
        raise HTTPException(status_code=ese.status_code, detail=ese.message)
    except UserError as une:
        raise HTTPException(status_code=une.status_code, detail=une.message)
    except Exception as e:
        print(e.__class__.__name__, e)
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
        print(e.__class__.__name__, e)
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
        print(e.__class__.__name__, e)
        raise HTTPException(status_code=401, detail="Token inválido")

    uid = payload["uid"]

    try:
        await auth_service.get_verification_code(uid=uid, code=payload["code"])
        user_data = await auth_service.change_password(uid=uid, new_password=update_password.new_password)
        return {"message": "Contraseña actualizada con éxito", "user": user_data}
    except AuthError as ae:
        raise HTTPException(status_code=ae.status_code, detail=ae.message)
    except UserError as ue:
        raise HTTPException(status_code=ue.status_code, detail=ue.message)
    except Exception as e:
        print(e.__class__.__name__, e)
        raise HTTPException(status_code=500, detail="Server error")

@auth_router.get("/github/login")
async def github_login():
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_CALLBACK_URL,
        "scope": "user:email",
        "allow_signup": "true"
    }
    url = f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

@auth_router.get("/github/callback")
async def github_callback(code: str, auth_service: AuthService = Depends(get_auth_service),
                          access_token: AccessToken = Depends(get_access_token)):
    token_url = "https://github.com/login/oauth/access_token"
    user_url = "https://api.github.com/user"
    emails_url = "https://api.github.com/user/emails"

    try:
        timeout = httpx.Timeout(10.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout, headers={"Accept": "application/json", "User-Agent": "backend-water-quality"}) as client:
            response = await client.post(
                token_url,
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": GITHUB_CALLBACK_URL,
                },
            )
            response.raise_for_status()
            token_data = response.json()
            github_token = token_data.get("access_token")
            if not github_token:
                raise HTTPException(status_code=400, detail="Error obteniendo token de GitHub")

            auth_headers = {"Authorization": f"Bearer {github_token}", "Accept": "application/json", "User-Agent": "backend-water-quality"}
            user_resp = await client.get(user_url, headers=auth_headers)
            user_resp.raise_for_status()
            github_user = user_resp.json()

            # Try to get a primary email if not returned in /user
            email = github_user.get("email")
            if not email:
                emails_resp = await client.get(emails_url, headers=auth_headers)
                if emails_resp.status_code == 200:
                    emails = emails_resp.json()
                    primary = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
                    email = primary or (github_user.get("login") + "@github.com")
                else:
                    email = github_user.get("login") + "@github.com"

            username = github_user.get("login")
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Tiempo de espera agotado al conectar con GitHub")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Tiempo de espera agotado en la solicitud a GitHub")
    except httpx.HTTPError as e:
        print(e.__class__.__name__, e)
        raise HTTPException(status_code=502, detail="Error al comunicarse con la API de GitHub")

    user = auth_service.user_repo.get_by_email(email)
    if not user:
        # Generate a secure random password to satisfy validation rules; not used for actual login
        generated_password = secrets.token_urlsafe(16)
        user_data = UserRegister(email=email, username=username, password=generated_password)
        user = await auth_service.register(user_data)

    normalized_role = user.rol.value if hasattr(user.rol, "value") else user.rol
    if isinstance(normalized_role, str) and normalized_role.startswith("Roles."):
        normalized_role = normalized_role.split(".", 1)[1].lower()
    payload = {"uid": user.uid, "email": user.email, "username": user.username, "rol": normalized_role, "exp": time.time() + 2592000}
    token = access_token.create(payload)

    if not FRONTEND_ORIGIN:
        # Si no está configurado, responde con JSON como fallback
        return {"message": "Logged in with GitHub", "user": user, "token": token}

    redirect_params = {
        "token": token,
        "email": user.email,
        "username": user.username,
        "rol": normalized_role,
        "uid": user.uid,
    }
    redirect_url = f"{FRONTEND_ORIGIN}?{urllib.parse.urlencode(redirect_params)}"
    print("Redirecting to:", redirect_url)
    return RedirectResponse(redirect_url, status_code=302)
