from fastapi import APIRouter, Depends, HTTPException

from app.features.workspaces.domain.model import Workspace, WorkspaceCreate, WorkspaceGuestCreate, WorkspaceGuestDelete, WorkspaceGuestUpdate
from app.features.workspaces.domain.response import ResponseGuest, ResponseGuests, ResponseWorkspacePublic, ResponseWorkspacesShares
from app.features.workspaces.infrastructure.repo_share_impl import WorkspaceGuestRepositoryImpl
from app.share.users.infra.users_repo_impl import UserRepositoryImpl
from app.share.workspace.workspace_access import WorkspaceAccess
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.features.workspaces.infrastructure.repo_impl import WorkspaceRepositoryImpl


workspaces_router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"]
)

user_repo = UserRepositoryImpl()
workspace_access = WorkspaceAccess(user_repo=user_repo)

workspace_repo = WorkspaceRepositoryImpl(
    access=workspace_access, user_repo=user_repo)


workspace_guest_repo = WorkspaceGuestRepositoryImpl(
    access=workspace_access, user_repo=user_repo)


@workspaces_router.get("/")
async def get_workspaces(user=Depends(verify_access_token)):

    data = workspace_repo.get_per_user(user.uid)
    print(data)
    return {"data": data}


@workspaces_router.get("/{id}")
async def get_workspace(id: str, user=Depends(verify_access_token)):
    try:
        data = workspace_repo.get_by_id(id, owner=user.uid)
        return {"data": data}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=ve.args[0])
    except HTTPException as he:
        raise he


@workspaces_router.get("/public/{workspace_id}/")
async def get_public_workspace(workspace_id: str) -> ResponseWorkspacePublic:
    try:
        result = workspace_repo.get_public(workspace_id)
        return ResponseWorkspacePublic(
            message="Workspace retrieved successfully",
            workspace=result
        )
    except ValueError as ve:
        print(ve)
        print(ve.args)
        raise HTTPException(status_code=404, detail="Error de validación")
    except HTTPException as he:
        raise he


@workspaces_router.post("/")
async def create_workspace(workspace: WorkspaceCreate, user=Depends(verify_access_token)):
    try:
        workspace_data = Workspace(name=workspace.name, owner=user.uid)
        new_workspace = workspace_repo.create(workspace_data)
        return {"data": new_workspace}
    except HTTPException as he:
        raise he


@workspaces_router.put("/{id}")
async def update_workspace(id: str, workspace: WorkspaceCreate, user=Depends(verify_access_token)):
    try:
        updated_workspace = workspace_repo.update(
            id, workspace, owner=user.uid)
        return {"data": updated_workspace}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except HTTPException as he:
        raise he


@workspaces_router.delete("/{id}")
async def delete_workspace(id: str, user=Depends(verify_access_token)):
    try:
        result = workspace_repo.delete(id, owner=user.uid)
        if not result:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return {"message": "Workspace deleted successfully"}
    except HTTPException as he:
        raise he


@workspaces_router.get("/share/")
async def get_share_workspace(user=Depends(verify_access_token)) -> ResponseWorkspacesShares:
    try:
        result = workspace_repo.get_workspaces_shares(user.uid)
        return ResponseWorkspacesShares(
            message="Shares retrieved successfully",
            workspaces=result
        )
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=404, detail="Error de validación")
    except HTTPException as he:
        raise he


@workspaces_router.get("/{id}/guest/")
async def get_guest_workspace(id: str, user=Depends(verify_access_token)) -> ResponseGuests:
    try:
        result = workspace_guest_repo.get_guest_workspace(id, user.uid)
        return ResponseGuests(
            message="Guests retrieved successfully",
            guests=result
        )
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=404, detail="Error de validación")
    except HTTPException as he:
        raise he


@workspaces_router.post("/{id}/guest/")
async def create_guest_workspace(id: str, workspace: WorkspaceGuestCreate, user=Depends(verify_access_token)) -> ResponseGuest:
    try:
        result = workspace_guest_repo.create(
            id_workspace=id, user=user.uid, workspace_share=workspace)
        return ResponseGuest(
            message="Guest created successfully",
            guest=result
        )
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
async def update_guest_workspace(id: str, guest: str, workspace: WorkspaceGuestUpdate, user=Depends(verify_access_token)) -> ResponseGuest:
    try:
        result = workspace_guest_repo.update(
            id_workspace=id, user=user.uid, guest=guest, share_update=workspace
        )

        return ResponseGuest(
            message="Guest updated successfully",
            guest=result
        )
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
async def delete_guest_workspace(id: str, guest: str, user=Depends(verify_access_token)) -> ResponseGuest:
    try:
        result = workspace_guest_repo.delete(
            WorkspaceGuestDelete(
                workspace_id=id,
                user=user.uid,
                guest=guest
            )
        )
        return ResponseGuest(
            message="Guest deleted successfully",
            guest=result
        )
    except HTTPException as he:
        raise he
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=400, detail="Error de validación")
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
