from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from app.share.depends import get_user_repo
from app.share.users.domain.repository import UserRepository
from app.share.jwt.domain.payload import UserPayload
from app.features.auth.domain.model import VerifyResetCode
from app.share.jwt.infrastructure.access_token import AccessToken
from app.features.auth.services.services import AuthService


@lru_cache()
def get_auth_service(user_repo: Annotated[UserRepository, Depends(get_user_repo)]):
    return AuthService(user_repo=user_repo)


@lru_cache()
def get_access_token() -> AccessToken:
    return AccessToken[UserPayload]()


@lru_cache()
def get_access_token_code() -> AccessToken:
    return AccessToken[VerifyResetCode]()
