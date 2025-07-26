import random
from datetime import datetime, timedelta
from firebase_admin import auth, db
import httpx
from app.features.auth.domain.errors import AuthError
from app.features.auth.domain.model import GenerateResetCode, VerifyResetCode
from app.share.firebase.domain.config import FirebaseConfigImpl
from app.share.users.domain.enum.roles import Roles
from app.share.users.domain.errors import UserError
from app.share.users.domain.model.auth import UserLogin, UserRegister
from app.share.users.domain.model.user import UserData
from app.share.users.domain.repository import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, user: UserRegister) -> UserData:
        user = self.user_repo.create_user(user=user, rol=Roles.CLIENT)
        return user

    async def login(self, user: UserLogin) -> UserData:
        config = FirebaseConfigImpl()
        api_key = config.api_key
        url_sign_in = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}'

        print(url_sign_in)
        
        auth_user = self.user_repo.get_by_email(user.email)

        print(auth_user)    
        
        if auth_user is None:
            raise AuthError(status_code=401, message="Usuario no registrado")
        
        body = {
            "email": user.email,
            "password": user.password,
        }

        async with httpx.AsyncClient() as client:
            # response = requests.post(url_sign_in, json=body)
            response = await client.post(url_sign_in, json=body)
            
            if response.status_code != 200:
                raise AuthError(
                    status_code=response.status_code, message="Credenciales inválidas")
            return auth_user

        

    async def generate_verification_code(self, email: str) -> GenerateResetCode:
        user = self.user_repo.get_by_email(email)
        if user is None:
            raise UserError(status_code=404, message="Usuario no registrado")

        reset_code = random.randint(100000, 999999)
        expire_date = datetime.now() + timedelta(minutes=10)

        db.reference(f"/password_reset/{user.uid}").set({
            "code": reset_code,
            "expires": expire_date.timestamp()
        })

        print(f"Temporal code is: {reset_code}")
        print(f"Temporal code Expires: {expire_date.timestamp()}")

        return GenerateResetCode(username=user.username, code=reset_code)

    async def get_verification_code(self, uid: str, code: int, user: UserData = None) -> VerifyResetCode:

        user = user or self.user_repo.get_by_uid(uid)

        if user is None:
            raise AuthError(status_code=404, message="Usuario no registrado")

        code_data = db.reference(f"/password_reset/{user.uid}/").get()

        if not code_data:
            raise AuthError(status_code=401,
                            message="Código de verificación inválido")

        verify_reset_code = VerifyResetCode(uid=user.uid, code=int(
            code_data.get("code")), exp=code_data.get("expires"))

        expire = datetime.fromtimestamp(verify_reset_code.exp)

        if datetime.now() > expire:
            raise AuthError(status_code=401, message="Código expirado")

        if verify_reset_code.code != code:
            raise AuthError(status_code=401,
                            message="Código de verificación inválido")

        return VerifyResetCode(uid=user.uid, code=code_data.get("code"), exp=code_data.get("expires"))

    async def verify_reset_code(self, email: str, code: int) -> VerifyResetCode:
        try:
            user = self.user_repo.get_by_email(email)
            if user is None:
                raise UserError(status_code=404,
                                message="Usuario no registrado")

            return await self.get_verification_code(uid=user.uid, code=code, user=user)
        except UserError as ue:
            raise AuthError(status_code=ue.status_code, message=ue.message)

    async def change_password(self, uid: str, new_password: str):

        user = self.user_repo.change_password(
            uid=uid, password=new_password)

        db.reference(f"/password_reset/{user.uid}/").delete()

        return user
