from fastapi import HTTPException
import random
from datetime import datetime, timedelta
from firebase_admin import auth, db
import httpx
from app.features.auth.domain.body import UpdatePassword
from app.features.auth.domain.model import VerifyResetCode
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

    async def generate_verification_code(self, email: str) -> int:
        user = self.user_repo.get_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        reset_code = random.randint(100000, 999999)
        expire_date = datetime.now() + timedelta(minutes=10)

        db.reference(f"/password_reset/{user.uid}").set({
            "code": reset_code,
            "expires": expire_date.timestamp()
        })

        print(f"Code: {reset_code}")
        print(f"Expires: {expire_date.timestamp()}")

        return reset_code

    async def get_verification_code(self, uid: str, code: int) -> VerifyResetCode:
        user = self.user_repo.get_by_uid(uid)
        if user is None:
            return None

        code_data = db.reference(f"/password_reset/{user.uid}/").get()

        if not code_data:
            return None

        verify_reset_code = VerifyResetCode(uid=user.uid, code=int(
            code_data.get("code")), exp=code_data.get("expires"))

        expire = datetime.fromtimestamp(verify_reset_code.exp)

        if datetime.now() > expire:
            return None

        if verify_reset_code.code != code:
            return None

        return VerifyResetCode(uid=user.uid, code=code_data.get("code"), exp=code_data.get("expires"))

    async def verify_reset_code(self, email: str, code: int) -> VerifyResetCode:
        return await self.get_verification_code(uid=self.user_repo.get_by_email(email).uid, code=code)

    async def change_password(self, uid: str, new_password: str):

        user = self.user_repo.change_password(
            uid=uid, password=new_password)

        db.reference(f"/password_reset/{user.uid}/").delete()

        return user
