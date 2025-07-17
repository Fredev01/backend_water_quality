from fastapi import HTTPException
from firebase_admin import auth
from app.share.users.domain.enum.roles import Roles
from app.share.users.domain.errors import UserError
from app.share.users.domain.model.auth import UserRegister
from app.share.users.domain.model.user import UserData, UserDetail, UserUpdate
from app.share.users.domain.repository import UserRepository


class UserRepositoryImpl(UserRepository):
    def get_by_uid(self, uid: str) -> UserData | None:
        """Obtiene un usuario por su UID."""
        try:
            auth_user: auth.UserRecord = auth.get_user(uid)
            return UserData(
                uid=auth_user.uid,
                username=auth_user.display_name,
                email=auth_user.email,
                phone=auth_user.phone_number,
                rol=auth_user.custom_claims.get("rol"),
            )
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            print(e.__class__.__name__)
            print(e)
            raise HTTPException(status_code=500, detail="Error del servidor")

    def create_user(self, user: UserRegister, rol: Roles) -> UserData:
        try:
            user_record: auth.UserRecord = auth.create_user(
                email=user.email,
                password=user.password,
                display_name=user.username,
                phone_number=user.phone,
            )
            auth.set_custom_user_claims(uid=user_record.uid, custom_claims={
                "rol": rol,
            })

            return UserData(
                uid=user_record.uid,
                username=user_record.display_name,
                email=user_record.email,
                phone=user_record.phone_number,
                rol=rol,
            )

        except auth.EmailAlreadyExistsError as eae:
            print(eae)
            raise UserError(status_code=400, message="Correo ya existe")
        except auth.PhoneNumberAlreadyExistsError:
            raise UserError(
                status_code=400, message="Número de teléfono ya existe")

    def get_by_email(self, email: str) -> UserData | None:
        try:
            auth_user: auth.UserRecord = auth.get_user_by_email(email)
            return UserData(
                uid=auth_user.uid,
                username=auth_user.display_name,
                email=auth_user.email,
                phone=auth_user.phone_number,
                rol=auth_user.custom_claims.get("rol"),
            )
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            print(e.__class__.__name__)
            print(e)
            raise HTTPException(status_code=500, detail="Error del servidor")

    def get_all(self, page_token: str = None) -> list[UserData]:
        users: auth.ListUsersPage = auth.list_users(page_token=page_token)
        return [
            UserData(
                uid=user.uid,
                username=user.display_name,
                email=user.email,
                phone=user.phone_number,
                rol=user.custom_claims.get("rol")
            )
            for user in users.users]

    def update_user(self, uid: str, user: UserUpdate) -> UserData:
        user_record: auth.UserRecord = auth.update_user(
            uid=uid,
            email=user.email,
            password=user.password,
            display_name=user.username,
            phone_number=user.phone
        )

        return UserData(
            email=user_record.email,
            username=user_record.display_name,
            phone=user_record.phone_number,
            uid=user_record.uid,
            rol=user_record.custom_claims.get("rol"),
        )

    def change_password(self, uid: str, password: str) -> UserData:
        user_record: auth.UserRecord = auth.update_user(
            uid=uid, password=password)

        return UserData(
            email=user_record.email,
            username=user_record.display_name,
            phone=user_record.phone_number,
            uid=user_record.uid,
            rol=user_record.custom_claims.get("rol"),
        )
