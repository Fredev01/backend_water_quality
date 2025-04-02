from abc import ABC, abstractmethod
from app.features.workspaces.domain.model import GuestResponse, WorkspaceCreate, WorkspaceGuestCreate, WorkspaceGuestDelete, WorkspaceGuestUpdate, WorkspacePublicResponse, WorkspaceShareResponse


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
    def update(self, id_workspace: str,  guest: str, share_update: WorkspaceCreate) -> GuestResponse:
        pass


class WorkspaceGuestRepository(ABC):
    @abstractmethod
    def get_guest_workspace(self, id_workspace: str, user: str) -> list[GuestResponse]:
        pass

    @abstractmethod
    def create(self, id_workspace: str, user: str, workspace_share: WorkspaceGuestCreate) -> GuestResponse:
        pass

    @abstractmethod
    def update(self, id_workspace: str, user: str, guest: str, share_update: WorkspaceGuestUpdate) -> GuestResponse:
        pass

    @abstractmethod
    def delete(self, workspace_delete: WorkspaceGuestDelete) -> GuestResponse:
        pass
