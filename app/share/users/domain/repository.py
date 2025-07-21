from abc import ABC, abstractmethod

from app.share.users.domain.enum.roles import Roles
from app.share.users.domain.model.auth import UserRegister
from app.share.users.domain.model.user import UserData, UserDetail, UserUpdate


class UserRepository(ABC):
    @abstractmethod
    def get_by_uid(self, uid: str,limit_data:bool=False) -> UserData:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> UserData:
        pass

    @abstractmethod
    def get_all(self) -> list[UserData]:
        """
        Retrieve all users.
        :return: List of UserDetail objects.
        """
        pass

    @abstractmethod
    def update_user(self, user: UserUpdate) -> UserData:
        """
        Update user details.
        :param user: UserDetail object with updated information.
        :return: Updated UserDetail object.
        """
        pass

    @abstractmethod
    def create_user(self, user: UserRegister, rol: Roles) -> UserData:
        """
        Create a new user.
        :param user: UserDetail object with user information.
        :return: Created UserDetail object.
        """
        pass

    @abstractmethod
    def change_password(self, uid: str, password: str) -> UserData:
        """
        Change user password.
        :param uid: User UID.
        :param password: New password.
        :return: Updated UserDetail object.
        """
        pass
