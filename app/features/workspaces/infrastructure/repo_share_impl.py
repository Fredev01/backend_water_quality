
from fastapi import HTTPException

from app.features.workspaces.domain.workspace_share_repo import WorkspaceGuestRepository
from app.features.workspaces.domain.model import GuestResponse,  WorkspaceGuestCreate, WorkspaceGuestDelete, WorkspaceGuestUpdate
from firebase_admin import db

from app.share.workspace.domain.model import WorkspaceRoles
from app.share.workspace.workspace_access import WorkspaceAccess


class WorkspaceGuestRepositoryImpl(WorkspaceGuestRepository):
    def __init__(self, access: WorkspaceAccess):
        self.access = access

    def _get_workspace_share_ref(self, id: str) -> db.Reference:
        workspaces_ref = db.reference().child('workspaces')
        workspace_ref = workspaces_ref.child(id)

        workspace_data = workspace_ref.get()

        if workspace_data is None:
            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {id}")

        return workspace_ref

    def _get_guest_role(self, id_workspace: str, guest: str) -> str:
        id_share_ref = db.reference().child(
            'guest_workspaces').child(self.access.safe_email(guest)).child(id_workspace)

        if id_share_ref.get() is None:
            raise HTTPException(
                status_code=403, detail=f"No tiene acceso a la workspace con ID: {id_workspace}")

        guest_rol = self._get_workspace_share_ref(id_workspace).child(
            "guests").child(self.access.safe_email(guest)).child("rol").get() or "unknown"

        return guest_rol

    def _get_workspace_ref(self, id: str, owner: str) -> db.Reference:

        workspaces_ref = self._get_workspace_share_ref(id)
        workspaces_data = workspaces_ref.get()

        if workspaces_data.get('owner') != owner:
            raise HTTPException(
                status_code=403, detail=f"No tiene acceso a la workspace con ID: {id}")

        return workspaces_ref

    def _check_workspace_access(self, id: str, user: str) -> tuple[db.Reference, WorkspaceRoles | None]:
        workspace_ref = self._get_workspace_share_ref(id)
        workspace_data = workspace_ref.get()

        if workspace_data.get('owner') == user:
            return workspace_ref, None

        guest_rol = self._get_guest_role(id, user)

        if guest_rol == WorkspaceRoles.ADMINISTRATOR.value:
            return workspace_ref, guest_rol

        raise HTTPException(
            status_code=403, detail=f"No tiene acceso a la workspace con ID: {id}")

    def get_guest_workspace(self, id_workspace: str, user: str) -> list[GuestResponse]:

        workspace_ref = self.access.get_ref(id_workspace, user, roles=[
                                            WorkspaceRoles.ADMINISTRATOR])

        guests_ref = workspace_ref.child('guests')

        guests_data = guests_ref.get()

        if guests_data is None:
            return []

        guests_list: list[GuestResponse] = []

        for guest_id, data in guests_data.items():
            guests_list.append(
                GuestResponse(
                    id=guest_id,
                    email=data["email"],
                    rol=data["rol"]
                )
            )

        return guests_list

    def create(self, id_workspace: str, user: str, workspace_share: WorkspaceGuestCreate) -> GuestResponse:
        workspace_ref = self.access.get_ref(id_workspace, user, roles=[
                                            WorkspaceRoles.ADMINISTRATOR])

        guests_ref = workspace_ref.child('guests')

        safe_email = self.access.safe_email(workspace_share.guest)

        guest_ref = guests_ref.child(safe_email)

        guests_exists = guest_ref.get() or {}

        if guests_exists:
            raise HTTPException(
                status_code=400, detail=f"El usuario {workspace_share.guest} ya está en el workspace")

        guest_ref.set({
            'email': workspace_share.guest,
            'rol': workspace_share.rol
        })

        guest_data = guest_ref.get()

        db.reference().child("guest_workspaces").child(
            safe_email).child(id_workspace).set(True)

        return GuestResponse(
            id=guest_ref.key,
            email=guest_data.get('email'),
            rol=guest_data.get('rol'),
        )

    def update(self, id_workspace: str, user: str, guest: str, share_update: WorkspaceGuestUpdate) -> GuestResponse:
        if user == guest:
            raise HTTPException(
                status_code=403, detail=f"No puedes cambiarte de acceso a ti mismo")

        workspace_ref = self.access.get_ref(id_workspace, user, roles=[
                                            WorkspaceRoles.ADMINISTRATOR])

        user_is_administrator = self.access.is_guest_rol(workspace_ref, user, roles=[
            WorkspaceRoles.ADMINISTRATOR])

        guest_is_administrator = self.access.is_guest_rol(workspace_ref, guest, roles=[
            WorkspaceRoles.ADMINISTRATOR])

        guests_ref = workspace_ref.child('guests')

        safe_email = self.access.safe_email(guest)

        guest_ref = guests_ref.child(safe_email)

        guest_data = guest_ref.get() or None

        if guest_data is None:
            raise HTTPException(
                status_code=404, detail=f"El usuario {guest} no está en el workspace")

        if user_is_administrator and guest_is_administrator:
            raise HTTPException(
                status_code=403, detail=f"No puedes cambiarle de acceso a este usuario: {id_workspace}")

        guest_ref.update({
            'rol': share_update.rol
        })

        guest_data = guest_ref.get()

        return GuestResponse(
            id=guest_ref.key,
            email=guest_data.get('email'),
            rol=guest_data.get('rol'),
        )

    def delete(self, workspace_delete: WorkspaceGuestDelete) -> GuestResponse:
        if workspace_delete.user == workspace_delete.guest:
            raise HTTPException(
                status_code=403, detail=f"No puedes eliminarte a ti mismo")

        workspace_ref = self.access.get_ref(workspace_delete.workspace_id, workspace_delete.user, roles=[
                                            WorkspaceRoles.ADMINISTRATOR])

        user_is_administrator = self.access.is_guest_rol(workspace_ref, workspace_delete.user, roles=[
            WorkspaceRoles.ADMINISTRATOR])

        guest_is_administrator = self.access.is_guest_rol(workspace_ref, workspace_delete.guest, roles=[
            WorkspaceRoles.ADMINISTRATOR])

        if user_is_administrator and guest_is_administrator:
            raise HTTPException(
                status_code=403, detail=f"No puedes eliminar a un administrador de un workspace")

        guests_ref = workspace_ref.child('guests')

        safe_email = self.access.safe_email(workspace_delete.id)

        guest_ref = guests_ref.child(safe_email)

        guest_data = guest_ref.get() or None

        if guest_data is None:
            raise HTTPException(
                status_code=404, detail=f"El usuario {workspace_delete.guest} no está en el workspace")

        guest_ref.delete()

        db.reference().child("guest_workspaces").child(
            safe_email).child(workspace_delete.workspace_id).delete()

        return GuestResponse(
            id=guest_ref.key,
            email=guest_data.get('email'),
            rol=guest_data.get('rol'),
        )
