from fastapi import APIRouter, Depends, HTTPException

from app.features.workspaces.domain.model import (
    Workspace,
    WorkspaceCreate,
    WorkspaceGuestCreate,
    WorkspaceGuestDelete,
    WorkspaceGuestUpdate,
)
from app.features.workspaces.domain.repository import WorkspaceRepository
from app.features.workspaces.domain.response import (
    ResponseGuest,
    ResponseGuests,
    ResponseWorkspacePublic,
    ResponseWorkspacesShares,
)
from app.features.workspaces.domain.workspace_share_repo import WorkspaceGuestRepository

from app.share.email.domain.repo import EmailRepository
from app.share.email.infra.html_template import HtmlTemplate
from app.share.email.presentation.depends import get_html_template, get_sender
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.verify_access_token import (
    verify_access_admin_token,
    verify_access_token,
)
from app.features.workspaces.presentation.depends import (
    get_workspace_repo,
    get_workspace_guest_repo,
)


workspaces_router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@workspaces_router.get("/")
async def get_workspaces(
    user: UserPayload = Depends(verify_access_token),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
):

    data = workspace_repo.get_per_user(user.uid)
    print(data)
    return {"data": data}


@workspaces_router.get("/all/")
async def get_all_workspaces(
    user: UserPayload = Depends(verify_access_admin_token),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
):
    try:
        data = workspace_repo.get_all()
        return {"workspaces": data}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@workspaces_router.get("/{id}")
async def get_workspace(
    id: str,
    user: UserPayload = Depends(verify_access_token),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
):
    try:
        data = workspace_repo.get_by_id(id, owner=user.uid)
        return {"data": data}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=ve.args[0])
    except HTTPException as he:
        raise he


@workspaces_router.get("/public/{workspace_id}/")
async def get_public_workspace(
    workspace_id: str, workspace_repo: WorkspaceRepository = Depends(get_workspace_repo)
) -> ResponseWorkspacePublic:
    try:
        result = workspace_repo.get_public(workspace_id)
        return ResponseWorkspacePublic(
            message="Workspace retrieved successfully", workspace=result
        )
    except ValueError as ve:
        print(ve)
        print(ve.args)
        raise HTTPException(status_code=404, detail="Error de validación")
    except HTTPException as he:
        raise he


@workspaces_router.post("/")
async def create_workspace(
    workspace: WorkspaceCreate,
    user: UserPayload = Depends(verify_access_token),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
):
    try:
        workspace_data = Workspace(name=workspace.name, owner=user.uid)
        new_workspace = workspace_repo.create(workspace_data)
        return {"data": new_workspace}
    except HTTPException as he:
        raise he


@workspaces_router.put("/{id}")
async def update_workspace(
    id: str,
    workspace: WorkspaceCreate,
    user: UserPayload = Depends(verify_access_token),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
):
    try:
        updated_workspace = workspace_repo.update(id, workspace, owner=user.uid)
        return {"data": updated_workspace}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except HTTPException as he:
        raise he


@workspaces_router.delete("/{id}")
async def delete_workspace(
    id: str,
    user: UserPayload = Depends(verify_access_token),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
):
    try:
        result = workspace_repo.delete(id, owner=user.uid)
        if not result:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return {"message": "Workspace deleted successfully"}
    except HTTPException as he:
        raise he


@workspaces_router.get("/share/")
async def get_share_workspace(
    user: UserPayload = Depends(verify_access_token),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
) -> ResponseWorkspacesShares:
    try:
        result = workspace_repo.get_workspaces_shares(user.uid)
        return ResponseWorkspacesShares(
            message="Shares retrieved successfully", workspaces=result
        )
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=404, detail="Error de validación")
    except HTTPException as he:
        raise he


@workspaces_router.get("/{id}/guest/")
async def get_guest_workspace(
    id: str,
    user: UserPayload = Depends(verify_access_token),
    workspace_guest_repo: WorkspaceGuestRepository = Depends(get_workspace_guest_repo),
) -> ResponseGuests:
    try:
        result = workspace_guest_repo.get_guest_workspace(id, user.uid)
        return ResponseGuests(message="Guests retrieved successfully", guests=result)
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=404, detail="Error de validación")
    except HTTPException as he:
        raise he


@workspaces_router.post("/{id}/guest/")
async def create_guest_workspace(
    id: str,
    workspace: WorkspaceGuestCreate,
    user: UserPayload = Depends(verify_access_token),
    workspace_guest_repo: WorkspaceGuestRepository = Depends(get_workspace_guest_repo),
    html_template: HtmlTemplate = Depends(get_html_template),
    sender: EmailRepository = Depends(get_sender),
) -> ResponseGuest:
    try:
        result = workspace_guest_repo.create(
            id_workspace=id, user=user.uid, workspace_share=workspace
        )

        body = html_template.get_guest_workspace(result.username, user.username, id)

        sender.send(
            to=result.email, subject="Invitación a espacio de trabajo", body=body
        )

        return ResponseGuest(message="Guest created successfully", guest=result)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@workspaces_router.put("/{id}/guest/{guest}")
async def update_guest_workspace(
    id: str,
    guest: str,
    workspace: WorkspaceGuestUpdate,
    user: UserPayload = Depends(verify_access_token),
    workspace_guest_repo: WorkspaceGuestRepository = Depends(get_workspace_guest_repo),
) -> ResponseGuest:
    try:
        result = workspace_guest_repo.update(
            id_workspace=id, user=user.uid, guest=guest, share_update=workspace
        )

        return ResponseGuest(message="Guest updated successfully", guest=result)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail="Validation error")
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@workspaces_router.delete("/{id}/guest/{guest}")
async def delete_guest_workspace(
    id: str,
    guest: str,
    user: UserPayload = Depends(verify_access_token),
    workspace_guest_repo: WorkspaceGuestRepository = Depends(get_workspace_guest_repo),
) -> ResponseGuest:
    try:
        result = workspace_guest_repo.delete(
            WorkspaceGuestDelete(workspace_id=id, user=user.uid, guest=guest)
        )
        return ResponseGuest(message="Guest deleted successfully", guest=result)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=400, detail="Error de validación")
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
