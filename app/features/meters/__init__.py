from fastapi import APIRouter, Depends, HTTPException
from app.features.meters.domain.model import WQMeterCreate
from app.features.workspaces.domain.response import WQMeterCreateResponse, WQMeterGetResponse

from app.features.meters.infrastructure.repo_meter_impl import WaterQualityMeterRepositoryImpl
from app.share.jwt.infrastructure.verify_access_token import verify_access_token


meters_router = APIRouter(
    prefix="/meters",
    tags=["Meters"]
)

water_quality_meter_repo = WaterQualityMeterRepositoryImpl()


@meters_router.get("/{id_workspace}/")
async def all(id_workspace: str, user=Depends(verify_access_token)) -> WQMeterGetResponse:
    try:
        data = water_quality_meter_repo.get_list(id_workspace, user.email)
        return WQMeterGetResponse(message="Meters retrieved successfully", meters=data)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=ve.args[0])
    except HTTPException as he:
        raise he
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@meters_router.post("/{id_workspace}/")
async def create(id_workspace: str, meter: WQMeterCreate, user=Depends(verify_access_token)) -> WQMeterCreateResponse:
    try:

        new_meter = water_quality_meter_repo.add(
            id_workspace, user.email, meter)
        return WQMeterCreateResponse(message="Meter created successfully", meter=new_meter)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
