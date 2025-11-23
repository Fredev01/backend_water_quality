from abc import ABC, abstractmethod
from typing import List
from .model import (
    WorkspaceCreate,
    WorkspacePublicResponse,
    WorkspaceResponse,
    WorkspaceShareResponse,
    WorskspacePagination,
)


class WorkspaceRepository(ABC):

    @abstractmethod
    def get_per_user(
        self, owner: str, pagination: WorskspacePagination
    ) -> List[WorkspaceResponse]:
        pass

    @abstractmethod
    def get_all(
        self,
        pagination: WorskspacePagination,
    ) -> List[WorkspaceResponse]:
        pass

    @abstractmethod
    def get_all_public(
        self, pagination: WorskspacePagination
    ) -> list[WorkspacePublicResponse]:
        pass

    @abstractmethod
    def get_workspaces_shares(
        self, user: str, pagination: WorskspacePagination
    ) -> list[WorkspaceShareResponse]:
        pass

    @abstractmethod
    def get_by_id(self, id: str, owner: str) -> WorkspaceResponse:
        pass

    @abstractmethod
    def create(self, workspace: WorkspaceCreate) -> WorkspaceResponse:
        pass

    @abstractmethod
    def update(
        self, id: str, workspace: WorkspaceCreate, owner: str
    ) -> WorkspaceResponse:
        pass

    @abstractmethod
    def delete(self, id: str, owner: str) -> bool:
        pass
