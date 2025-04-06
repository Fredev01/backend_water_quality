from fastapi import HTTPException
from firebase_admin import db

from app.features.workspaces.domain.model import WorkspaceRoles, WorkspaceType


class WorkspaceAccess:
    def safe_email(self, email: str) -> str:
        return email.lower().replace('.', ',')

    def recover_email(self, email: str) -> str:
        return email.replace(',', '.')

    def is_guest_rol(self, workspace_ref: db.Reference, user: str, roles: list[WorkspaceRoles]) -> bool:
        return workspace_ref.child("guests").child(self.safe_email(user)).child("rol").get() in roles

    def get_ref(self, workspace_id: str, user: str, roles: list[WorkspaceRoles] = [], is_public: bool = False) -> db.Reference:
        workspaces_ref = db.reference().child('workspaces').child(workspace_id)
        workspaces = workspaces_ref.get()

        if workspaces is None:
            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {workspace_id}")

        if is_public and workspaces.get('type') == WorkspaceType.PUBLIC:
            return workspaces_ref

        if workspaces.get('owner') == user:
            return workspaces_ref

        guest_role = self.is_guest_rol(
            workspaces_ref, user=user, roles=roles)

        if guest_role:
            return workspaces_ref

        raise HTTPException(
            status_code=403, detail=f"No tiene acceso a la workspace con ID: {workspace_id}")
