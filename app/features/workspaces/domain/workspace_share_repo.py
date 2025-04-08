from abc import ABC, abstractmethod
from app.features.workspaces.domain.model import GuestResponse, WorkspaceGuestCreate, WorkspaceGuestDelete, WorkspaceGuestUpdate


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
