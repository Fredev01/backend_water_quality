from fastapi import HTTPException
from firebase_admin import auth
import httpx
from app.share.firebase.domain.config import FirebaseConfigImpl
from app.share.users.domain.enum.roles import Roles
from app.share.users.domain.model.auth import UserLogin, UserRegister
from app.share.users.domain.model.user import UserData, UserDetail
from app.share.users.domain.repository import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, user: UserRegister) -> UserData:
        user = self.user_repo.create_user(user=user, rol=Roles.CLIENT)
        return user

    async def login(self, user: UserLogin) -> UserData:

        try:
            config = FirebaseConfigImpl()
            api_key = config.api_key
            url_sign_in = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}'
            print(url_sign_in)

            auth_user = self.user_repo.get_by_email(user.email)

            body = {
                "email": user.email,
                "password": user.password,
            }

            async with httpx.AsyncClient() as client:
                # response = requests.post(url_sign_in, json=body)
                response = await client.post(url_sign_in, json=body)

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=400, detail="Invalid credentials")

                return auth_user

        except auth.UserNotFoundError:
            raise HTTPException(status_code=401, detail="Unregistered user")
        except Exception as e:
            print(e.__class__.__name__)
            print(e)
            raise HTTPException(status_code=500, detail="Server error")

    async def send_reset_password(self, email: str) -> str:
        config = FirebaseConfigImpl()
        api_key = config.api_key
        url_reset = f'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}'

        body = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url_reset, json=body)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Failed to send reset email")

            return {"message": "Password reset email sent"}
