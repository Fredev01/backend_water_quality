from fastapi import HTTPException
from app.features.workspaces.domain.repository import WorkspaceRepository
from firebase_admin import db
from app.features.workspaces.domain.model import Workspace, WorkspaceCreate, WorkspacePublicResponse, WorkspaceResponse, WorkspaceShareResponse

from typing import List

from app.share.workspace.domain.model import WorkspaceRoles
from app.share.workspace.workspace_access import WorkspaceAccess


class WorkspaceRepositoryImpl(WorkspaceRepository):
    def __init__(self, access: WorkspaceAccess):
        self.access = access

    def get_per_user(self, owner: str) -> List[WorkspaceResponse]:
        """Obtiene todos los workspaces pertenecientes a un usuario."""
        workspaces_ref = db.reference().child('workspaces')
        workspaces_query = workspaces_ref.order_by_child(
            'owner').equal_to(owner).get() or {}

        workspaces = []
        for workspace_id, data in workspaces_query.items():
            workspace = WorkspaceResponse(
                id=workspace_id,
                name=data['name'],
                owner=data['owner'],
                type=data['type']
            )
            workspaces.append(workspace)
        return workspaces

    def get_by_id(self, id: str, owner: str) -> WorkspaceResponse:
        """Obtiene un workspace por su ID."""
        workspace_ref = self.access.get_ref(workspace_id=id, user=owner, roles=[
                                            WorkspaceRoles.VISITOR, WorkspaceRoles.MANAGER, WorkspaceRoles.ADMINISTRATOR])
        workspace_data = workspace_ref.get()

        return WorkspaceResponse(
            id=id,
            name=workspace_data.get('name'),
            owner=workspace_data.get('owner'),
            type=workspace_data.get('type')
        )

    def get_public(self, workspace_id: str) -> WorkspacePublicResponse:
        """Obtiene un workspace público por su ID."""
        workspace_ref = self.access.get_ref(
            workspace_id=workspace_id, user=None, is_public=True)
        workspace_data = workspace_ref.get()
        print(workspace_data.get('type'))

        return WorkspacePublicResponse(
            id=workspace_id,
            name=workspace_data.get('name')
        )

    def _get_workspace_share_ref(self, id: str) -> db.Reference:
        workspaces_ref = db.reference().child('workspaces')
        workspace_ref = workspaces_ref.child(id)

        workspace_data = workspace_ref.get()

        if workspace_data is None:
            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {id}")

        return workspace_ref

    def get_workspaces_shares(self, guest: str) -> list[WorkspaceShareResponse]:

        workspace_ids_ref = db.reference().child(
            'guest_workspaces').child(self.access.safe_email(guest))

        workspace_list: list[WorkspaceShareResponse] = []

        for workspace_id in workspace_ids_ref.get().keys():
            workspace = self._get_workspace_share_ref(workspace_id)

            workspace_data = workspace.get()
            guest_data = workspace.child('guests').child(
                self.access.safe_email(guest)).get()

            workspace_list.append(WorkspaceShareResponse(
                id=workspace_id,
                name=workspace_data.get('name'),
                owner=workspace_data.get('owner'),
                guest=guest_data.get('email'),
                rol=guest_data.get('rol'),
            ))

        return workspace_list

    def create(self, workspace: Workspace) -> WorkspaceResponse:
        """Crea un nuevo workspace."""
        workspaces_ref = db.reference().child('workspaces')
        workspace_dict = workspace.model_dump()
        new_workspace_ref = workspaces_ref.push(workspace_dict)
        return WorkspaceResponse(
            id=new_workspace_ref.key,
            **workspace_dict,
        )

    def delete(self, id: str, owner: str) -> bool:
        """Elimina un workspace por su ID."""

        try:
            workspace_ref = self.access.get_ref(workspace_id=id, user=owner)
            if workspace_ref.get() is None:
                return False
            workspace_ref.delete()
            return True
        except Exception:
            return False

    def update(self, id: str, workspace: WorkspaceCreate, owner: str) -> WorkspaceResponse:
        """Actualiza un workspace existente."""

        workspace_ref = self.access.get_ref(
            workspace_id=id, user=owner, roles=[WorkspaceRoles.ADMINISTRATOR])

        update_data = workspace.model_dump()
        workspace_ref.update(update_data)
        updated_data = workspace_ref.get()
        return WorkspaceResponse(
            id=id,
            name=updated_data.get('name'),
            owner=updated_data.get('owner'),
            type=updated_data.get('type')
        )
