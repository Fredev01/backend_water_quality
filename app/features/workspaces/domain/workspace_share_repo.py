from abc import ABC, abstractmethod
from app.features.workspaces.domain.model import GuestResponse, WorkspaceGuestCreate, WorkspaceGuestDelete, WorkspaceGuestUpdate, WorkspacePublicResponse, WorkspaceShareResponse


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


class WorkspaceGuestRepository(ABC):
    @abstractmethod
    def get_guest_workspace(self, workspace_id: str, owner: str) -> list[GuestResponse]:
        pass

    @abstractmethod
    def create(self, workspace_create: WorkspaceGuestCreate) -> GuestResponse:
        pass

    @abstractmethod
    def update(self, id_workspace: str, owner: str, guest: str, share_update: WorkspaceGuestUpdate) -> GuestResponse:
        pass

    @abstractmethod
    def delete(self, workspace_delete: WorkspaceGuestDelete) -> GuestResponse:
        pass
