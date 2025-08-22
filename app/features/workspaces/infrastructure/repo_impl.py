from typing import List
from firebase_admin import db
from app.features.workspaces.domain.repository import WorkspaceRepository
from app.features.workspaces.domain.model import (
    Workspace,
    WorkspaceCreate,
    WorkspacePublicResponse,
    WorkspaceResponse,
    WorkspaceShareResponse,
)
from app.share.users.domain.repository import UserRepository
from app.share.workspace.domain.model import WorkspaceRoles, WorkspaceRolesAll
from app.share.workspace.workspace_access import WorkspaceAccess


class WorkspaceRepositoryImpl(WorkspaceRepository):
    def __init__(self, access: WorkspaceAccess, user_repo: UserRepository):
        self.access = access
        self.user_repo = user_repo

    def get_all(self) -> List[WorkspaceResponse]:

        workspaces_ref = db.reference().child("workspaces")

        workspaces = []
        for workspace_id, data in workspaces_ref.get().items():
            user_detail = self.user_repo.get_by_uid(data.get("owner"))
            workspace = WorkspaceResponse(
                id=workspace_id,
                name=data.get("name"),
                owner=data.get("owner"),
                user=user_detail,
                type=data.get("type"),
                rol=WorkspaceRolesAll.OWNER,
            )
            workspaces.append(workspace)
        return workspaces

    def get_per_user(self, owner: str) -> List[WorkspaceResponse]:
        """Obtiene todos los workspaces pertenecientes a un usuario."""
        workspaces_ref = db.reference().child("workspaces")
        workspaces_query = (
            workspaces_ref.order_by_child("owner").equal_to(owner).get() or {}
        )

        workspaces = []
        for workspace_id, data in workspaces_query.items():
            user_detail = self.user_repo.get_by_uid(data.get("owner"))

            workspace = WorkspaceResponse(
                id=workspace_id,
                name=data.get("name"),
                owner=data.get("owner"),
                type=data.get("type"),
                user=user_detail,
                rol=WorkspaceRolesAll.OWNER,
            )
            workspaces.append(workspace)
        return workspaces

    def get_by_id(self, id: str, owner: str) -> WorkspaceResponse:
        """Obtiene un workspace por su ID."""
        workspace_ref = self.access.get_ref(
            workspace_id=id,
            user=owner,
            roles=[
                WorkspaceRoles.VISITOR,
                WorkspaceRoles.MANAGER,
                WorkspaceRoles.ADMINISTRATOR,
            ],
        )
        workspace_data = workspace_ref.ref.get()

        return WorkspaceResponse(
            id=id,
            name=workspace_data.get("name"),
            owner=workspace_data.get("owner"),
            type=workspace_data.get("type"),
            rol=workspace_ref.rol,
        )

    def get_public(self, workspace_id: str) -> WorkspacePublicResponse:
        """Obtiene un workspace público por su ID."""
        workspace_ref = self.access.get_ref(
            workspace_id=workspace_id, user=None, is_public=True
        )
        workspace_data = workspace_ref.ref.get()

        return WorkspacePublicResponse(id=workspace_id, name=workspace_data.get("name"))

    def get_workspaces_shares(self, user: str) -> list[WorkspaceShareResponse]:

        workspace_ids_ref = db.reference().child("guest_workspaces").child(user)

        print(workspace_ids_ref.get())

        workspace_list: list[WorkspaceShareResponse] = []

        if workspace_ids_ref.get() is None:
            print("No hay workspaces compartidos")
            return workspace_list

        for workspace_id in workspace_ids_ref.get().keys():
            workspace_reference = self.access.get_ref(
                workspace_id=workspace_id,
                user=user,
                roles=[
                    WorkspaceRoles.VISITOR,
                    WorkspaceRoles.MANAGER,
                    WorkspaceRoles.ADMINISTRATOR,
                ],
                is_null=True,
            )

            if workspace_reference is None:
                continue

            workspace_ref = workspace_reference.ref

            guest_user = self.user_repo.get_by_uid(user)

            workspace_data = workspace_ref.get()

            user_detail = self.user_repo.get_by_uid(
                workspace_data.get("owner"), limit_data=True
            )

            workspace_list.append(
                WorkspaceShareResponse(
                    id=workspace_id,
                    name=workspace_data.get("name"),
                    owner=workspace_data.get("owner"),
                    guest=workspace_reference.user.email,
                    user=user_detail,
                    rol=workspace_reference.rol,
                )
            )

        return workspace_list

    def create(self, workspace: Workspace) -> WorkspaceResponse:
        """Crea un nuevo workspace."""
        workspaces_ref = db.reference().child("workspaces")
        workspace_dict = workspace.model_dump()
        new_workspace_ref = workspaces_ref.push(workspace_dict)
        return WorkspaceResponse(
            id=new_workspace_ref.key,
            **workspace_dict,
        )

    def delete(self, id: str, owner: str) -> bool:
        """Elimina un workspace por su ID."""

        try:
            workspace_ref = self.access.get_ref(workspace_id=id, user=owner).ref
            if workspace_ref.get() is None:
                return False
            workspace_ref.delete()
            return True
        except Exception:
            return False

    def update(
        self, id: str, workspace: WorkspaceCreate, owner: str
    ) -> WorkspaceResponse:
        """Actualiza un workspace existente."""

        workspace_ref = self.access.get_ref(
            workspace_id=id, user=owner, roles=[WorkspaceRoles.ADMINISTRATOR]
        ).ref

        update_data = workspace.model_dump()
        workspace_ref.update(update_data)
        updated_data = workspace_ref.get()
        return WorkspaceResponse(
            id=id,
            name=updated_data.get("name"),
            owner=updated_data.get("owner"),
            type=updated_data.get("type"),
        )
