import time
from fastapi import APIRouter, Depends, HTTPException
from app.features.meters.domain.model import SensorIdentifier, SensorQueryParams, WQMeterCreate, WQMeterUpdate
from app.features.meters.infrastructure.meter_records_impl import MeterRecordsRepositoryImpl
from app.features.meters.infrastructure.repo_connect_impl import WaterQMConnectionImpl
from app.features.meters.domain.response import WQMeterGetResponse, WQMeterRecordsResponse, WQMeterResponse, WQMeterSensorRecordsResponse

from app.features.meters.infrastructure.repo_meter_impl import WaterQualityMeterRepositoryImpl
from app.features.meters.services.meter_records_service import MeterRecordsService
from app.features.workspaces.infrastructure.authorization_service_impl import WorkspaceAuthorizationServiceImpl
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
    meter_repo=water_quality_meter_repo)
meter_records_repo = MeterRecordsRepositoryImpl()
workspace_auth_service = WorkspaceAuthorizationServiceImpl()
meter_records_service = MeterRecordsService(repository=meter_records_repo, auth_service=workspace_auth_service)

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
async def create(id_workspace: str, meter: WQMeterCreate, user=Depends(verify_access_token)) -> WQMeterResponse:
    try:

        new_meter = water_quality_meter_repo.add(
            id_workspace, user.email, meter)
        return WQMeterResponse(message="Meter created successfully", meter=new_meter)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@meters_router.put("/{id_workspace}/{id_meter}/")
async def update(id_workspace: str, id_meter: str, meter: WQMeterUpdate, user=Depends(verify_access_token)) -> WQMeterResponse:
    try:
        meter_update = water_quality_meter_repo.update(
            id_workspace=id_workspace, owner=user.email, id_meter=id_meter, meter=meter)
        return WQMeterResponse(message="Meter updated successfully", meter=meter_update)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server Error")


@meters_router.put("/{id_workspace}/status/{id_meter}/")
async def status(id_workspace: str, id_meter: str, user=Depends(verify_access_token)) -> WQMeterResponse:
    try:
        meter_update = water_quality_meter_repo.set_status(
            id_workspace=id_workspace, owner=user.email, id_meter=id_meter)
        return WQMeterResponse(message="Meter updated successfully", meter=meter_update)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server Error")


@meters_router.delete("/{id_workspace}/{id_meter}/")
async def delete(id_workspace: str, id_meter: str, user=Depends(verify_access_token)):
    try:
        meter = water_quality_meter_repo.delete(
            id_workspace=id_workspace, owner=user.email, id_meter=id_meter)
        return WQMeterResponse(message="Meter deleted successfully", meter=meter)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server Error")


@meters_router.post("/{id_workspace}/connect/{id_meter}/")
async def connect(id_workspace: str,  id_meter: str, user=Depends(verify_access_token)):
    try:
        password = meter_connection.create(
            id_workspace, user.email, id_meter)
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

@meters_router.get("/{id_workspace}/{id_meter}/")
async def get_records_meter(id_workspace: str, id_meter: str, user=Depends(verify_access_token)):
    try:
        identifier = SensorIdentifier(meter_id=id_meter, workspace_id=id_workspace, user_id=user.email)
        meter_records = meter_records_service.get_10_last_sensor_records(identifier)
        return WQMeterRecordsResponse(message="Records retrieved successfully", records=meter_records)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=ve.args[0])
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail="Meter not exists")
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")

@meters_router.get("/{id_workspace}/{id_meter}/{sensor_name}/")
async def get_sensor_records(id_workspace: str, id_meter: str, sensor_name: str, limit: int = 10,
                            descending: bool = True,convert_timestamp: bool = False, user=Depends(verify_access_token)):
    try:
        identifier = SensorIdentifier(meter_id=id_meter, workspace_id=id_workspace, user_id=user.email, sensor_name=sensor_name)
        params = SensorQueryParams(limit=limit, descending=descending, convert_timestamp=convert_timestamp)
        sensor_records = meter_records_service.get_sensor_records(identifier, params)
        return WQMeterSensorRecordsResponse(message="Records retrieved successfully", records=sensor_records)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")