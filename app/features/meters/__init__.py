import time
from fastapi import APIRouter, Depends, HTTPException
from app.features.meters.domain.model import WQMeterCreate
from app.features.meters.infrastructure.repo_connect_impl import WaterQMConnectionImpl
from app.features.meters.domain.response import WQMeterCreateResponse, WQMeterGetResponse

from app.features.meters.infrastructure.repo_meter_impl import WaterQualityMeterRepositoryImpl
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.share.jwt.domain.payload import MeterPayload
from app.share.jwt.infrastructure.access_token import AccessToken

meters_router = APIRouter(
    prefix="/meters",
    tags=["Meters"]
)


access_token_connection = AccessToken[MeterPayload]()


water_quality_meter_repo = WaterQualityMeterRepositoryImpl()
meter_connection = WaterQMConnectionImpl(
    water_quality_meter_repo=water_quality_meter_repo)


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


@meters_router.post("/{id_workspace}/connect/{id_meter}/")
async def connect(id_workspace: str,  id_meter: str, user=Depends(verify_access_token)):
    try:
        password = meter_connection.create(
            id_workspace, user.email, id_workspace)
        return {"password": password}
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@meters_router.get("/receive/{password}/")
async def connect(password: int):
    try:
        meter = meter_connection.receive(password)

        if meter is None:
            raise HTTPException(status_code=400, detail="No existe conexión")

        payload = MeterPayload(
            id_workspace=meter.id_workspace,
            owner=meter.owner,
            id_meter=meter.id_meter,
            exp=time.time() + 2592000
        ).model_dump()

        token = access_token_connection.create(payload=payload)

        meter_connection.delete(meter.id)

        return {"message": "Conexión recibida", "token": token}
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
