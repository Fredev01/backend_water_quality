from fastapi import APIRouter, Depends, Request, HTTPException
import jwt

from app.features.workspaces.domain.model import Workspace, WorkspaceCreate
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.features.workspaces.infrastructure.repo_impl import WorkspaceRepositoryImpl


workspaces_router = APIRouter(
    prefix="/workspaces",
)

workspace_repo = WorkspaceRepositoryImpl()

@workspaces_router.get("/")
async def get_workspaces(user=Depends(verify_access_token)):
    print(user)
    data = workspace_repo.get_per_user(user.email)
    return {"data": data}

@workspaces_router.get("/{id}")
async def get_workspace(id: str, user=Depends(verify_access_token)):
    try:
        data = workspace_repo.get_by_id(id)
        return {"data": data}
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
        workspace_data = Workspace(name=workspace.name, owner=user.email)
        updated_workspace = workspace_repo.update(id, workspace_data)
        return {"data": updated_workspace}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except HTTPException as he:
        raise he

@workspaces_router.delete("/{id}")
async def delete_workspace(id: str, user=Depends(verify_access_token)):
    try:
        result = workspace_repo.delete(id)
        if not result:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return {"message": "Workspace deleted successfully"}
    except HTTPException as he:
        raise he
