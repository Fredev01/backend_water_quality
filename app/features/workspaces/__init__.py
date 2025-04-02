from fastapi import APIRouter, Depends, HTTPException

from app.features.workspaces.domain.model import Workspace, WorkspaceCreate, WorkspaceGuestCreate, WorkspaceGuestDelete, WorkspaceGuestUpdate
from app.features.workspaces.infrastructure.repo_share_impl import WorkspaceGuestRepositoryImpl, WorkspaceShareRepositoryImpl
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.features.workspaces.infrastructure.repo_impl import WorkspaceRepositoryImpl


workspaces_router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"]
)

workspace_repo = WorkspaceRepositoryImpl()
workspace_share_repo = WorkspaceShareRepositoryImpl(
    workspace_repo=workspace_repo)

workspace_guest_repo = WorkspaceGuestRepositoryImpl()


@workspaces_router.get("/")
async def get_workspaces(user=Depends(verify_access_token)):
    print(user)
    data = workspace_repo.get_per_user(user.email)
    return {"data": data}


@workspaces_router.get("/{id}")
async def get_workspace(id: str, user=Depends(verify_access_token)):
    try:
        data = workspace_repo.get_by_id(id, owner=user.email)
        return {"data": data}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=ve.args[0])
    except HTTPException as he:
        raise he


@workspaces_router.post("/")
async def create_workspace(workspace: WorkspaceCreate, user=Depends(verify_access_token)):
    try:
        workspace_data = Workspace(name=workspace.name, owner=user.email)
        new_workspace = workspace_repo.create(workspace_data)
        return {"data": new_workspace}
    except HTTPException as he:
        raise he


@workspaces_router.put("/{id}")
async def update_workspace(id: str, workspace: WorkspaceCreate, user=Depends(verify_access_token)):
    try:
        updated_workspace = workspace_repo.update(
            id, workspace, owner=user.email)
        return {"data": updated_workspace}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except HTTPException as he:
        raise he


@workspaces_router.delete("/{id}")
async def delete_workspace(id: str, user=Depends(verify_access_token)):
    try:
        result = workspace_repo.delete(id, owner=user.email)
        if not result:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return {"message": "Workspace deleted successfully"}
    except HTTPException as he:
        raise he


@workspaces_router.get("/share/")
async def get_share_workspace(user=Depends(verify_access_token)):
    try:
        data = workspace_share_repo.get_workspaces_shares(user.email)
        return {"data": data}
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=404, detail="Error de validación")
    except HTTPException as he:
        raise he


@workspaces_router.get("/share/{id}")
async def get_share_workspace(id: str, user=Depends(verify_access_token)):
    try:
        data = workspace_share_repo.get_workspace_share(user.email, id)
        return {"data": data}
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=404, detail="Error de validación")
    except HTTPException as he:
        raise he


@workspaces_router.put("/share/{id_workspace}")
async def update_share_workspace(id_workspace: str, workspace: WorkspaceCreate, user=Depends(verify_access_token)):
    try:
        data = workspace_share_repo.update(
            id_workspace=id_workspace, guest=user.email, share_update=workspace)
        return {"data": data}
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=404, detail="Error de validación")
    except HTTPException as he:
        raise he


@workspaces_router.get("/{id}/guest/")
async def get_guest_workspace(id: str, user=Depends(verify_access_token)):
    try:
        data = workspace_guest_repo.get_guest_workspace(id, user.email)
        return {"data": data}
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=404, detail="Error de validación")
    except HTTPException as he:
        raise he


@workspaces_router.post("/{id}/guest/")
async def create_guest_workspace(id: str, workspace: WorkspaceGuestCreate, user=Depends(verify_access_token)):
    try:
        workspace_share = workspace_guest_repo.create(
            id_workspace=id, owner=user.email, workspace_share=workspace)
        return {"data": workspace_share}
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
async def update_guest_workspace(id: str, guest: str, workspace: WorkspaceGuestUpdate, user=Depends(verify_access_token)):
    try:
        workspace_share = workspace_guest_repo.update(
            id_workspace=id, owner=user.email, guest=guest, share_update=workspace
        )

        return {"data": workspace_share.model_dump()}
    except HTTPException as he:
        raise he
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@workspaces_router.delete("/{id}/guest/{guest}")
async def delete_guest_workspace(id: str, guest: str, user=Depends(verify_access_token)):
    try:
        workspace_share = workspace_guest_repo.delete(
            WorkspaceGuestDelete(
                id=guest,
                workspace_id=id,
                owner=user.email,
                guest=guest
            )
        )
        return {"data": workspace_share.model_dump()}
    except HTTPException as he:
        raise he
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=400, detail="Error de validación")
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@workspaces_router.get("/public/{workspace_id}")
async def get_public_workspace(workspace_id: str):
    try:
        data = workspace_share_repo.get_workspace_public(workspace_id)
        return {"data": data}
    except ValueError as ve:
        print(ve.args)
        raise HTTPException(status_code=404, detail="Error de validación")
    except HTTPException as he:
        raise he
