
from fastapi import HTTPException
from app.features.workspaces.domain.workspace_share_repo import WorkspaceGuestRepository, WorkspaceShareRepository
from app.features.workspaces.domain.model import GuestResponse, WorkspaceGuestCreate, WorkspaceGuestDelete, WorkspaceGuestUpdate, WorkspacePublicResponse, WorkspaceShareResponse, WorkspaceType
from firebase_admin import db


def _safe_email(email: str) -> str:
    return email.lower().replace('.', ',')


def _recover_email(email: str) -> str:
    return email.replace(',', '.')


class WorkspaceShareRepositoryImpl(WorkspaceShareRepository):

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


class WorkspaceGuestRepositoryImpl(WorkspaceGuestRepository):
    def _get_workspace_ref(self, id: str, owner: str) -> db.Reference:

        workspaces_ref = db.reference().child('workspaces')
        workspace_ref = workspaces_ref.child(id)

        workspace_data = workspace_ref.get()

        if workspace_data is None:
            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {id}")

        if workspace_data.get('owner') != owner:
            raise HTTPException(
                status_code=403, detail=f"No tiene acceso a la workspace con ID: {id}")

        return workspace_ref

    def get_guest_workspace(self, workspace_id: str, owner: str) -> list[GuestResponse]:

        workspace_ref = self._get_workspace_ref(workspace_id, owner)

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

    def create(self, id_workspace: str, owner: str, workspace_share: WorkspaceGuestCreate) -> GuestResponse:
        workspace_ref = self._get_workspace_ref(
            id=id_workspace, owner=owner)

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

    def update(self, id_workspace: str, owner: str, guest: str, share_update: WorkspaceGuestUpdate) -> GuestResponse:

        workspace_ref = self._get_workspace_ref(
            id=id_workspace, owner=owner)

        guests_ref = workspace_ref.child('guests')

        safe_email = _safe_email(guest)

        guest_ref = guests_ref.child(safe_email)

        guests_exists = guest_ref.get() or None

        if guests_exists is None:
            raise HTTPException(
                status_code=404, detail=f"El usuario {guest} no está en el workspace")

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
