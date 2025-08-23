from fastapi import HTTPException
from firebase_admin import db

from app.share.users.domain.enum.roles import Roles
from app.share.users.domain.repository import UserRepository
from app.share.workspace.domain.model import (
    WorkspaceRef,
    WorkspaceGuest,
    WorkspaceRoles,
    WorkspaceRolesAll,
    WorkspaceType,
)


class WorkspaceAccess:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def is_guest_rol(
        self, workspace_ref: db.Reference, user: str, roles: list[WorkspaceRoles]
    ) -> WorkspaceGuest:
        """Get if the user has a role in the workspace.

        Args:
            workspace_ref (db.Reference): The reference to the workspace.
            user (str): The email of the user.
            roles (list[WorkspaceRoles]): List of roles that have access to the workspace.

        Returns:
            bool: True if the user has a role in the workspace, False otherwise.

        """
        rol = workspace_ref.child("guests").child(user).child("rol").get()
        return WorkspaceGuest(
            is_guest=rol in roles,
            rol=WorkspaceRoles(rol) if rol else WorkspaceRolesAll.UNKNOWN,
        )

    def get_ref(
        self,
        workspace_id: str,
        user: str | None,
        roles: list[WorkspaceRoles] = [],
        is_public: bool = False,
        is_null=False,
    ) -> WorkspaceRef | None:
        workspaces_ref = db.reference().child("workspaces").child(workspace_id)
        workspaces = workspaces_ref.get()

        if workspaces is None:
            if is_null:
                return None
            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {workspace_id}"
            )

        # Verificar si es público
        is_workspace_public = workspaces.get("type") == WorkspaceType.PUBLIC
        user_role = WorkspaceRoles.VISITOR
        user_detail = None

        # Si hay usuario, obtener su rol real
        if user:
            user_detail = self.user_repo.get_by_uid(user)

            # Verificar si es admin o dueño
            if user_detail.rol == Roles.ADMIN or workspaces.get("owner") == user:
                user_role = WorkspaceRolesAll.OWNER
            else:
                # Verificar rol de invitado
                workspace_guest = self.is_guest_rol(
                    workspaces_ref, user=user, roles=roles
                )
                if workspace_guest.is_guest:
                    user_role = workspace_guest.rol
                    # Si tiene rol de invitado válido, retornar referencia inmediatamente
                    return WorkspaceRef(
                        ref=workspaces_ref,
                        rol=user_role,
                        user=user_detail,
                        is_public=is_workspace_public,
                    )

        # Si el workspace es público, retornar referencia
        if is_public and is_workspace_public:
            return WorkspaceRef(
                ref=workspaces_ref,
                rol=user_role,
                is_public=True,
                user=user_detail,
            )

        # Si es owner, retornar referencia
        if user_role == WorkspaceRolesAll.OWNER:
            return WorkspaceRef(
                ref=workspaces_ref,
                rol=user_role,
                user=user_detail,
                is_public=is_workspace_public,
            )

        # Si no tiene ningún acceso válido
        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la workspace con ID: {workspace_id}",
        )
