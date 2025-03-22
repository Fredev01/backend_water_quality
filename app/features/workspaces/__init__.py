from fastapi import APIRouter, Depends, Request, HTTPException

from app.features.workspaces.domain.meter_model import WQMeterCreate
from app.features.workspaces.domain.model import Workspace, WorkspaceCreate
from app.features.workspaces.infrastructure.repo_meter_impl import WaterQualityMeterRepositoryImpl
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.features.workspaces.infrastructure.repo_impl import WorkspaceRepositoryImpl


workspaces_router = APIRouter(
    prefix="/workspaces",
    tags=["workspaces"]
)

workspace_repo = WorkspaceRepositoryImpl()

water_quality_meter_repo = WaterQualityMeterRepositoryImpl()


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


@workspaces_router.get("/{id}/meters/")
async def get_meters(id: str, user=Depends(verify_access_token)):
    try:
        data = water_quality_meter_repo.get_list(id, user.email)
        return {"data": data}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=ve.args[0])
    except HTTPException as he:
        raise he
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@workspaces_router.post("/{id}/meters/")
async def create_meter(id: str, meter: WQMeterCreate, user=Depends(verify_access_token)):
    try:

        new_meter = water_quality_meter_repo.add(id, user.email, meter)
        return {"data": new_meter}
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
