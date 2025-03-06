import jwt
from typing import TypeVar, Generic

from app.share.jwt.domain.config import JWTConfigImpl


config = JWTConfigImpl()

T = TypeVar('T')


class AccessToken(Generic[T]):
    def create(self, payload: T):
        return jwt.encode(
            payload,
            config.secret_key,
            algorithm='HS256'
        )

    def validate(self, token: str) -> dict:
        payload = jwt.decode(token, config.secret_key,
                             algorithms=['HS256'])
        return payload
