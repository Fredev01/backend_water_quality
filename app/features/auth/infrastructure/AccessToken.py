import jwt

from app.features.auth.domain.model import TokenPayload


class AccessToken:
    def create(self, payload: TokenPayload):
        return jwt.encode(
            payload,
            'secret',
            algorithm='HS256'
        )

    def validate(token) -> TokenPayload:
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return {'message': 'Token is expired'}
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}
        except Exception as e:
            return {'message': str(e)}
