
from fastapi import HTTPException
from app.features.workspaces.domain.repository import WorkspaceRepository
from app.features.workspaces.domain.workspace_share_repo import WorkspaceShareRepository
from app.features.workspaces.domain.model import GuestResponse, WorkspacePublicResponse,  WorkspaceShareCreate, WorkspaceShareDelete, WorkspaceShareResponse, WorkspaceShareUpdate
from firebase_admin import db


class WorkspaceShareRepositoryImpl(WorkspaceShareRepository):

    def _get_workspace_share_ref(self, id: str) -> db.Reference:
        workspaces_ref = db.reference().child('workspaces')
        workspace_ref = workspaces_ref.child(id)

        workspace_data = workspace_ref.get()

        if workspace_data is None:
            raise ValueError(f"No existe workspace con ID: {id}")

        return workspace_ref

    def _get_workspace_ref(self, id: str, owner: str) -> db.Reference:

        workspace_ref = self._get_workspace_share_ref(id)
        workspace_data = workspace_ref.get()

        if workspace_data.get('owner') != owner:
            raise ValueError(f"No existe workspace con ID: {id}")

        return workspace_ref

    def _get_id_share(self, guest: str, id_workspace: str) -> db.Reference:
        id_share_ref = db.reference().child(
            'guest_workspaces').child(self._safe_email(guest)).child(id_workspace)

        return id_share_ref

    def _safe_email(self, email: str) -> str:
        return email.lower().replace('.', ',')

    def _recover_email(self, email: str) -> str:
        return email.replace(',', '.')

    def get_workspaces_shares(self, guest: str) -> list[WorkspaceShareResponse]:

        workspace_ids_ref = db.reference().child(
            'guest_workspaces').child(self._safe_email(guest))

        workspace_list: list[WorkspaceShareResponse] = []

        for workspace_id in workspace_ids_ref.get().keys():
            workspace = self._get_workspace_share_ref(workspace_id)

            workspace_data = workspace.get()
            guest_data = workspace.child('guests').child(
                self._safe_email(guest)).get()

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
            self._safe_email(guest)).get()

        return WorkspaceShareResponse(
            id=id_share_ref.key,
            name=workspace_share_data.get('name'),
            owner=workspace_share_data.get('owner'),
            guest=guest_data.get('email'),
            rol=guest_data.get('rol'),
        )

    def get_workspace_public(self, workspace_id: str) -> WorkspacePublicResponse:
        return WorkspacePublicResponse()

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

    def create(self, id_workspace: str, owner: str, workspace_share: WorkspaceShareCreate) -> WorkspaceShareResponse:
        workspace_ref = self._get_workspace_ref(
            id=id_workspace, owner=owner)

        guests_ref = workspace_ref.child('guests')

        safe_email = self._safe_email(workspace_share.guest)

        guest_ref = guests_ref.child(safe_email)

        guests_exists = guest_ref.get() or {}

        if guests_exists:
            raise HTTPException(
                status_code=400, detail=f"El usuario {workspace_share.guest} ya está en el workspace")

        guest_ref.set({
            'email': workspace_share.guest,
            'rol': workspace_share.rol
        })

        workspace_data = workspace_ref.get()
        guest_data = guest_ref.get()

        db.reference().child("guest_workspaces").child(
            safe_email).child(id_workspace).set(True)

        return WorkspaceShareResponse(
            id=guest_ref.key,
            owner=owner,
            name=workspace_data.get('name'),
            guest=guest_data.get('email'),
            rol=guest_data.get('rol'),
        )

    def update(self, id_workspace: str, owner: str, guest: str, share_update: WorkspaceShareUpdate) -> WorkspaceShareResponse:

        workspace_ref = self._get_workspace_ref(
            id=id_workspace, owner=owner)

        guests_ref = workspace_ref.child('guests')

        safe_email = self._safe_email(guest)

        guest_ref = guests_ref.child(safe_email)

        guests_exists = guest_ref.get() or None

        if guests_exists is None:
            raise HTTPException(
                status_code=404, detail=f"El usuario {guest} no está en el workspace")

        guest_ref.update({
            'rol': share_update.rol
        })

        workspace_data = workspace_ref.get()
        guest_data = guest_ref.get()

        print(guest_data, guest_ref.key)

        return WorkspaceShareResponse(
            id=guest_ref.key,
            owner=owner,
            name=workspace_data.get('name'),
            guest=guest_data.get('email'),
            rol=guest_data.get('rol'),
        )

    def delete(self, workspace_delete: WorkspaceShareDelete) -> WorkspaceShareResponse:

        workspace_ref = self._get_workspace_ref(
            id=workspace_delete.workspace_id, owner=workspace_delete.owner)

        guests_ref = workspace_ref.child('guests')

        safe_email = self._safe_email(workspace_delete.id)

        guest_ref = guests_ref.child(safe_email)

        guest_data = guest_ref.get() or None

        if guest_data is None:
            raise HTTPException(
                status_code=404, detail=f"El usuario {workspace_delete.guest} no está en el workspace")

        guest_ref.delete()

        db.reference().child("guest_workspaces").child(
            safe_email).child(workspace_delete.workspace_id).delete()

        return WorkspaceShareResponse(
            id=guest_ref.key,
            owner=workspace_delete.owner,
            name=workspace_ref.get().get('name'),
            guest=workspace_delete.guest,
            rol=guest_data.get('rol'),
        )
