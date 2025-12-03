from typing import List
from firebase_admin import db
from app.features.workspaces.domain.repository import WorkspaceRepository
from app.features.workspaces.domain.model import (
    Workspace,
    WorkspaceCreate,
    WorkspacePublicResponse,
    WorkspaceResponse,
    WorkspaceShareResponse,
    WorskspacePagination,
)
from app.share.users.domain.repository import UserRepository
from app.share.workspace.domain.model import (
    WorkspaceRoles,
    WorkspaceRolesAll,
    WorkspaceType,
)
from app.share.workspace.workspace_access import WorkspaceAccess


class WorkspaceRepositoryImpl(WorkspaceRepository):
    def __init__(self, access: WorkspaceAccess, user_repo: UserRepository):
        self.access = access
        self.user_repo = user_repo

    def get_all(self, pagination: WorskspacePagination) -> List[WorkspaceResponse]:

        ref = db.reference().child("workspaces").order_by_key()

        workspaces_dict = self._pagination_from_query(ref, pagination)

        workspaces = []
        for workspace_id, data in workspaces_dict.items():
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

    def _pagination_from_query(
        self, query: db.Query, pagination: WorskspacePagination
    ) -> dict:
        if pagination.index is not None:
            workspaces_ref = query.start_at(pagination.index).limit_to_first(
                pagination.limit + 1
            )
            items = list(workspaces_ref.get().items())
            filtered = [item for item in items if item[0] != pagination.index]
            workspaces_dict = dict(filtered)

        else:
            workspaces_ref = query.limit_to_first(pagination.limit)
            workspaces_dict = workspaces_ref.get() or {}

        return workspaces_dict

    def _pagination_from_dict(
        self, workspace_dict: dict, pagination: WorskspacePagination
    ) -> dict:
        workspaces_query = {}
        if pagination.index is not None:
            keys = list(workspace_dict.keys())
            try:
                start_pos = keys.index(pagination.index) + 1
            except ValueError:
                start_pos = 0
            selected_keys = keys[start_pos : start_pos + pagination.limit]
            workspaces_query = {k: workspace_dict[k] for k in selected_keys}
        else:
            first_keys = list(workspace_dict.keys())[: pagination.limit]
            workspaces_query = {k: workspace_dict[k] for k in first_keys}
        return workspaces_query

    def get_per_user(
        self, owner: str, pagination: WorskspacePagination
    ) -> List[WorkspaceResponse]:
        """Obtiene todos los workspaces pertenecientes a un usuario."""
        workspaces_ref = db.reference().child("workspaces")
        workspaces_dict = (
            workspaces_ref.order_by_child("owner").equal_to(owner).get() or {}
        )

        workspaces_query = self._pagination_from_dict(workspaces_dict, pagination)

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
            is_public=True,
        )
        workspace_data = workspace_ref.ref.get()

        work_type = workspace_data.get("type")

        if (
            work_type == WorkspaceType.PUBLIC
            and workspace_ref.rol == WorkspaceRoles.VISITOR
        ):
            return WorkspaceResponse(
                id=id,
                name=workspace_data.get("name"),
                owner=None,
                type=workspace_data.get("type"),
                rol=workspace_ref.rol,
            )

        return WorkspaceResponse(
            id=id,
            name=workspace_data.get("name"),
            owner=workspace_data.get("owner"),
            type=workspace_data.get("type"),
            rol=workspace_ref.rol,
        )

    def get_all_public(
        self, pagination: WorskspacePagination
    ) -> list[WorkspacePublicResponse]:
        """Obtiene todos los workspaces públicos."""
        ref = db.reference().child("workspaces")

        all_public = (
            ref.order_by_child("type").equal_to(WorkspaceType.PUBLIC.value).get() or {}
        )

        workspaces_query = self._pagination_from_dict(all_public, pagination)

        workspaces = []
        for workspace_id, data in workspaces_query.items():
            workspace = WorkspacePublicResponse(
                id=workspace_id,
                name=data.get("name"),
                rol=WorkspaceRoles.VISITOR,
            )
            workspaces.append(workspace)

        return workspaces

    def get_workspaces_shares(
        self, user: str, pagination: WorskspacePagination
    ) -> list[WorkspaceShareResponse]:

        ref = db.reference().child("guest_workspaces").child(user).order_by_key()

        workspace_list: list[WorkspaceShareResponse] = []

        workspaces_query = self._pagination_from_query(ref, pagination)

        for workspace_id in workspaces_query.keys():
            workspace_reference = self.access.get_ref(
                workspace_id=workspace_id,
                user=user,
                roles=[
                    WorkspaceRoles.VISITOR,
                    WorkspaceRoles.MANAGER,
                    WorkspaceRoles.ADMINISTRATOR,
                ],
                is_null=True,
                owner_limit_data=True,
            )

            if workspace_reference is None:
                continue

            workspace_ref = workspace_reference.ref

            workspace_data = workspace_ref.get()

            workspace_list.append(
                WorkspaceShareResponse(
                    id=workspace_id,
                    name=workspace_data.get("name"),
                    owner=workspace_data.get("owner"),
                    type=workspace_data.get("type"),
                    guest=workspace_reference.user.email,
                    user=workspace_reference.owner,
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
            rol=WorkspaceRolesAll.OWNER,
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
            rol=WorkspaceRolesAll.OWNER,
        )
