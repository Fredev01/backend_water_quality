from abc import ABC, abstractmethod
from typing import List
from .model import (
    WorkspaceCreate,
    WorkspacePublicResponse,
    WorkspaceResponse,
    WorkspaceShareResponse,
)


class WorkspaceRepository(ABC):

    @abstractmethod
    def get_per_user(self, owner: str) -> List[WorkspaceResponse]:
        pass

    @abstractmethod
    def get_all(self) -> List[WorkspaceResponse]:
        pass

    @abstractmethod
    def get_public(self, workspace_id: str) -> WorkspacePublicResponse:
        pass

    @abstractmethod
    def get_workspaces_shares(self, user: str) -> list[WorkspaceShareResponse]:
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
