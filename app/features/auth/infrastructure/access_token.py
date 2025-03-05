import time
import jwt

from app.features.auth.domain.model import UserData, UserPayload


class AccessToken:
    def create(self, data: UserData):
        # expira el token en 1 hora
        payload = UserPayload(
            email=data.email,
            password=data.password,
            username=data.username,
            phone=data.phone,
            rol=data.rol,
            exp=time.time() + 3600
        ).model_dump()

        return jwt.encode(
            payload,
            'secret',
            algorithm='HS256'
        )

    def validate(token) -> UserPayload:
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return {'message': 'Token is expired'}
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}
        except Exception as e:
            return {'message': str(e)}
