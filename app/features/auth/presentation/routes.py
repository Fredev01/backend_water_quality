import time
import random
from datetime import datetime, timedelta
import urllib.parse
import httpx
import os
import secrets
import hmac
import hashlib
import base64
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Optional

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
APP_DEEP_LINK = os.environ.get("APP_DEEP_LINK", "aquaminds://login-success")
STATE_SECRET = os.environ.get("STATE_SECRET")

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


def sign_state(payload: dict) -> str:
    if not STATE_SECRET:
        raise HTTPException(status_code=500, detail="STATE_SECRET not configured")
    data = json.dumps(payload, separators=(",", ":")).encode()
    sig = hmac.new(STATE_SECRET.encode(), data, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(data + b"." + sig).decode().rstrip("=")
    return token


def verify_state(token: str) -> dict:
    if not STATE_SECRET:
        raise HTTPException(status_code=500, detail="STATE_SECRET not configured")
    pad = "=" * (-len(token) % 4)
    raw = base64.urlsafe_b64decode(token + pad)
    data, sig = raw.rsplit(b".", 1)
    exp_sig = hmac.new(STATE_SECRET.encode(), data, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, exp_sig):
        raise HTTPException(status_code=400, detail="invalid state signature")
    payload = json.loads(data.decode())
    if "exp" in payload and payload["exp"] < int(time.time()):
        raise HTTPException(status_code=400, detail="state expired")
    return payload


def is_mobile_scheme(uri: Optional[str]) -> bool:
    return bool(uri and uri.startswith(APP_DEEP_LINK))

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
async def github_login(redirect_uri: Optional[str] = None):
    # Whitelist allowed redirect destinations
    allowed = {FRONTEND_ORIGIN, APP_DEEP_LINK, None}
    if redirect_uri not in allowed:
        raise HTTPException(status_code=400, detail="redirect_uri not allowed")

    # Sign state with redirect_uri and expiration (10 minutes)
    state_payload = {
        "redirect_uri": redirect_uri,
        "exp": int(time.time()) + 600,
    }
    state = sign_state(state_payload)

    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_CALLBACK_URL,
        "scope": "user:email",
        "allow_signup": "true",
        "state": state,
    }
    url = f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

@auth_router.get("/github/login")
async def github_login_generic():
    # Relative redirect to avoid absolute localhost and preserve host/port
    return RedirectResponse(url="/auth/github/login/web", status_code=307)

@auth_router.get("/github/login/mobile")
async def github_login_mobile():
    # Fixed deep link for mobile
    state_payload = {
        "redirect_uri": APP_DEEP_LINK,
        "exp": int(time.time()) + 600,
    }
    state = sign_state(state_payload)

    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_CALLBACK_URL,
        "scope": "user:email",
        "allow_signup": "true",
        "state": state,
    }
    url = f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

@auth_router.get("/github/login/web")
async def github_login_web():
    if not FRONTEND_ORIGIN:
        raise HTTPException(status_code=500, detail="FRONTEND_ORIGIN not configured")

    state_payload = {
        "redirect_uri": FRONTEND_ORIGIN,
        "exp": int(time.time()) + 600,
    }
    state = sign_state(state_payload)

    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_CALLBACK_URL,
        "scope": "user:email",
        "allow_signup": "true",
        "state": state,
    }
    url = f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

@auth_router.get("/github/callback")
async def github_callback(
    request: Request,
    code: str,
    state: Optional[str] = None,
    auth_service: AuthService = Depends(get_auth_service),
    access_token: AccessToken = Depends(get_access_token),
):
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

    # Decide redirect based on signed state (preferred), fallback to web if not provided
    redirect_uri_from_state: Optional[str] = None
    if state:
        try:
            payload_state = verify_state(state)
            redirect_uri_from_state = payload_state.get("redirect_uri")
        except HTTPException:
            redirect_uri_from_state = None

    if is_mobile_scheme(redirect_uri_from_state):
        # Mobile deep link with token and code
        redirect_url = f"{APP_DEEP_LINK}?token={token}&code={code}"
    else:
        if not FRONTEND_ORIGIN:
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


@auth_router.get("/test/deeplink")
async def test_deeplink():
    # Simple 302 to test Android/iOS deep link handling independent of OAuth
    test_url = f"{APP_DEEP_LINK}?token=TEST"
    return RedirectResponse(test_url, status_code=302)
