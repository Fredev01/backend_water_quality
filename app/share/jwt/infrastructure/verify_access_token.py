import time
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Security
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.access_token import AccessToken
import jwt

from app.share.users.domain.enum.roles import Roles


access_token = AccessToken[UserPayload]()


security = HTTPBearer()


async def verify_access_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> UserPayload:
    token = credentials.credentials
    try:
        decoded_token = access_token.validate(token)

        user_payload = UserPayload(**decoded_token)

        return user_payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    except Exception as e:
        print(e)
        print(e.__class__.__name__)
        raise HTTPException(status_code=500, detail="Error en el token")


async def verify_access_admin_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> UserPayload:
    user_payload = await verify_access_token(credentials)
    if user_payload.rol != Roles.ADMIN:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para acceder a este recurso.")
    return user_payload
