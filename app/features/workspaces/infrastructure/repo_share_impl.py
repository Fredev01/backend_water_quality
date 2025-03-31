
from app.features.workspaces.domain.workspace_share_repo import WorkspaceShareRepository
from app.features.workspaces.domain.model import WorkspacePublicResponse,  WorkspaceShareCreate, WorkspaceShareDelete, WorkspaceShareResponse, WorkspaceShareUpdate


class WorkspaceShareRepositoryImpl(WorkspaceShareRepository):
    def get_workspaces_shares(self, guest: str) -> list[WorkspaceShareResponse]:
        return []

    def get_workspace_share(self, guest: str, workspace_id: str) -> WorkspaceShareResponse:
        return WorkspaceShareResponse()

    def get_workspace_public(self, workspace_id: str) -> WorkspacePublicResponse:
        return WorkspacePublicResponse()

    def create(self, workspace_create: WorkspaceShareCreate) -> WorkspaceShareResponse:
        return WorkspaceShareResponse()

    def update(self, workspace_update: WorkspaceShareUpdate) -> WorkspaceShareResponse:
        return WorkspaceShareResponse()

    def delete(self, workspace_delete: WorkspaceShareDelete) -> WorkspaceShareResponse:
        return WorkspaceShareResponse()
