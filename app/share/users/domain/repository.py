from abc import ABC, abstractmethod

from app.share.users.domain.model.user import UserDetail, UserUpdate


class UserRepository(ABC):
    @abstractmethod
    def get_by_uid(self, uid: str) -> UserDetail:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> UserDetail:
        pass

    @abstractmethod
    def get_all(self) -> list[UserDetail]:
        """
        Retrieve all users.
        :return: List of UserDetail objects.
        """
        pass

    @abstractmethod
    def update_user(self, user: UserUpdate) -> UserDetail:
        """
        Update user details.
        :param user: UserDetail object with updated information.
        :return: Updated UserDetail object.
        """
        pass
