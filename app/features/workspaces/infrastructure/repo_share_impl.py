
from fastapi import HTTPException
from app.features.workspaces.domain.repository import WorkspaceRepository
from app.features.workspaces.domain.workspace_share_repo import WorkspaceGuestRepository, WorkspaceShareRepository
from app.features.workspaces.domain.model import GuestResponse, WorkspaceCreate, WorkspaceGuestCreate, WorkspaceGuestDelete, WorkspaceGuestUpdate, WorkspacePublicResponse, WorkspaceResponse, WorkspaceRoles, WorkspaceShareResponse, WorkspaceType
from firebase_admin import db


def _safe_email(email: str) -> str:
    return email.lower().replace('.', ',')


def _recover_email(email: str) -> str:
    return email.replace(',', '.')


class WorkspaceShareRepositoryImpl(WorkspaceShareRepository):
    def __init__(self, workspace_repo: WorkspaceRepository):
        self.workspace_repo = workspace_repo

    def _get_workspace_share_ref(self, id: str) -> db.Reference:
        workspaces_ref = db.reference().child('workspaces')
        workspace_ref = workspaces_ref.child(id)

        workspace_data = workspace_ref.get()

        if workspace_data is None:
            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {id}")

        return workspace_ref

    def _get_workspace_ref(self, id: str, owner: str) -> db.Reference:

        workspace_ref = self._get_workspace_share_ref(id)
        workspace_data = workspace_ref.get()

        if workspace_data.get('owner') != owner:
            raise HTTPException(
                status_code=403, detail=f"No tiene acceso a la workspace con ID: {id}")

        return workspace_ref

    def _get_id_share(self, guest: str, id_workspace: str) -> db.Reference:
        id_share_ref = db.reference().child(
            'guest_workspaces').child(_safe_email(guest)).child(id_workspace)

        return id_share_ref

    def get_workspaces_shares(self, guest: str) -> list[WorkspaceShareResponse]:

        workspace_ids_ref = db.reference().child(
            'guest_workspaces').child(_safe_email(guest))

        workspace_list: list[WorkspaceShareResponse] = []

        for workspace_id in workspace_ids_ref.get().keys():
            workspace = self._get_workspace_share_ref(workspace_id)

            workspace_data = workspace.get()
            guest_data = workspace.child('guests').child(
                _safe_email(guest)).get()

            workspace_list.append(WorkspaceShareResponse(
                id=workspace_id,
                name=workspace_data.get('name'),
                owner=workspace_data.get('owner'),
                guest=guest_data.get('email'),
                rol=guest_data.get('rol'),
            ))

        return workspace_list

    def get_workspace_share(self, guest: str, workspace_id: str) -> WorkspaceShareResponse:
        id_share_ref = self._get_id_share(guest, workspace_id)

        if id_share_ref.get() is None:
            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {workspace_id}")

        workspace_share = self._get_workspace_share_ref(id_share_ref.key)

        workspace_share_data = workspace_share.get()

        guest_data = workspace_share.child('guests').child(
            _safe_email(guest)).get()

        return WorkspaceShareResponse(
            id=id_share_ref.key,
            name=workspace_share_data.get('name'),
            owner=workspace_share_data.get('owner'),
            guest=guest_data.get('email'),
            rol=guest_data.get('rol'),
        )

    def get_workspace_public(self, workspace_id: str) -> WorkspacePublicResponse:

        workspace_ref = self._get_workspace_share_ref(workspace_id)

        workspace_data = workspace_ref.get()

        if workspace_data is None:
            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {workspace_id}")

        if workspace_data.get('type') != WorkspaceType.PUBLIC:
            raise HTTPException(
                status_code=403, detail=f"No es un workspace público")

        return WorkspacePublicResponse(
            id=workspace_id,
            name=workspace_data.get('name'),
        )

    def update(self, id_workspace: str,  guest: str, share_update: WorkspaceCreate) -> WorkspaceResponse:
        id_share_ref = self._get_id_share(guest, id_workspace)

        if id_share_ref.get() is None:
            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {id_workspace}")

        workspace_share_ref = self._get_workspace_share_ref(
            id_share_ref.key)
        workspace_share = workspace_share_ref.get()

        if workspace_share is None:
            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {id_workspace}")

        guest_rol = workspace_share_ref.child("guests").child(
            _safe_email(guest)).child("rol").get() or ""

        owner = workspace_share.get("owner")

        if guest_rol != WorkspaceRoles.ADMINISTRATOR.value:
            raise HTTPException(
                status_code=403, detail=f"No tiene permiso para editar el workspace con ID: {id_workspace}")

        return self.workspace_repo.update(
            id=id_workspace, workspace=share_update, owner=owner)


class WorkspaceGuestRepositoryImpl(WorkspaceGuestRepository):
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
            'guest_workspaces').child(_safe_email(guest)).child(id_workspace)

        if id_share_ref.get() is None:
            raise HTTPException(
                status_code=403, detail=f"No tiene acceso a la workspace con ID: {id_workspace}")

        guest_rol = self._get_workspace_share_ref(id_workspace).child(
            "guests").child(_safe_email(guest)).child("rol").get() or "unknown"

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

        workspace_ref, user_rol = self._check_workspace_access(
            id=id_workspace, user=user)

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
        workspace_ref, user_rol = self._check_workspace_access(
            id=id_workspace, user=user)

        guests_ref = workspace_ref.child('guests')

        safe_email = _safe_email(workspace_share.guest)

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

        workspace_ref, user_rol = self._check_workspace_access(
            id=id_workspace, user=user)

        guests_ref = workspace_ref.child('guests')

        safe_email = _safe_email(guest)

        guest_ref = guests_ref.child(safe_email)

        guest_data = guest_ref.get() or None

        if guest_data is None:
            raise HTTPException(
                status_code=404, detail=f"El usuario {guest} no está en el workspace")

        if user_rol == WorkspaceRoles.ADMINISTRATOR and guest_data.get('rol') == WorkspaceRoles.ADMINISTRATOR.value:
            raise HTTPException(
                status_code=403, detail=f"No puedes cambiarle de acceso a este usuario: {id_workspace}")

        guest_ref.update({
            'rol': share_update.rol
        })

        guest_data = guest_ref.get()

        print(guest_data, guest_ref.key)

        return GuestResponse(
            id=guest_ref.key,
            email=guest_data.get('email'),
            rol=guest_data.get('rol'),
        )

    def delete(self, workspace_delete: WorkspaceGuestDelete) -> GuestResponse:

        workspace_ref = self._get_workspace_ref(
            id=workspace_delete.workspace_id, owner=workspace_delete.owner)

        guests_ref = workspace_ref.child('guests')

        safe_email = _safe_email(workspace_delete.id)

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
