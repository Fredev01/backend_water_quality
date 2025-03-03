import jwt

from app.features.auth.domain.model import TokenPayload


class AccessToken:
    def create(self, payload: TokenPayload):
        return jwt.encode(
            payload,
            'secret',
            algorithm='HS256'
        )
