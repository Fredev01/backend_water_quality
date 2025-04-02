from abc import ABC, abstractmethod
from app.features.workspaces.domain.model import GuestResponse, WorkspacePublicResponse,  WorkspaceShareCreate, WorkspaceShareDelete, WorkspaceShareResponse, WorkspaceShareUpdate


class WorkspaceShareRepository(ABC):
    @abstractmethod
    def get_workspaces_shares(self, guest: str) -> list[WorkspaceShareResponse]:
        pass

    @abstractmethod
    def get_workspace_share(self, guest: str, workspace_id: str) -> WorkspaceShareResponse:
        pass

    @abstractmethod
    def get_workspace_public(self, workspace_id: str) -> WorkspacePublicResponse:
        pass

    @abstractmethod
    def get_guest_workspace(self, workspace_id: str, owner: str) -> list[GuestResponse]:
        pass

    @abstractmethod
    def create(self, workspace_create: WorkspaceShareCreate) -> WorkspaceShareResponse:
        pass

    @abstractmethod
    def update(self, workspace_update: WorkspaceShareUpdate) -> WorkspaceShareResponse:
        pass

    @abstractmethod
    def delete(self, workspace_delete: WorkspaceShareDelete) -> WorkspaceShareResponse:
        pass
