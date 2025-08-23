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
        """Get a reference to a workspace.

        Args:
            workspace_id (str): The ID of the workspace.
            user (str): The email of the user.
            roles (list[WorkspaceRoles], optional): List of roles that have access to the workspace. Defaults to [].
            is_public (bool, optional): If the workspace is public, it returns directly and does not validate the user role.. Defaults to False.

        Returns:
            db.Reference: The reference to the workspace.

        """
        workspaces_ref = db.reference().child("workspaces").child(workspace_id)
        workspaces = workspaces_ref.get()

        if workspaces is None:
            if is_null:
                return None

            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {workspace_id}"
            )

        if is_public and workspaces.get("type") == WorkspaceType.PUBLIC:
            return WorkspaceRef(
                ref=workspaces_ref, rol=WorkspaceRoles.VISITOR, is_public=True
            )
        elif is_public and user is None:
            raise HTTPException(
                status_code=403,
                detail=f"La workspace con ID: {workspace_id} no es pública",
            )

        user_detail = self.user_repo.get_by_uid(user)
        # print(f"User role: {user_detail.rol}")

        if user_detail.rol == Roles.ADMIN or workspaces.get("owner") == user:
            return WorkspaceRef(
                ref=workspaces_ref, user=user_detail, rol=WorkspaceRolesAll.OWNER
            )

        workspace_guest = self.is_guest_rol(workspaces_ref, user=user, roles=roles)

        # print(guest_role)

        if workspace_guest.is_guest:
            return WorkspaceRef(
                ref=workspaces_ref,
                user=user_detail,
                rol=workspace_guest.rol,
            )

        raise HTTPException(
            status_code=403,
            detail=f"No tiene acceso a la workspace con ID: {workspace_id}",
        )
