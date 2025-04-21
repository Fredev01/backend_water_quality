import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.features.meters.domain.model import WQMeterCreate, WQMeterUpdate
from fastapi import APIRouter, Depends, HTTPException
from app.features.meters.domain.model import SensorIdentifier, SensorQueryParams, WQMeterCreate, WQMeterUpdate
from app.features.meters.infrastructure.meter_records_impl import MeterRecordsRepositoryImpl
from app.features.meters.infrastructure.repo_connect_impl import WaterQMConnectionImpl
from app.features.meters.domain.response import WQMeterConnectResponse, WQMeterGetResponse, WQMeterPasswordResponse, WQMeterRecordsResponse, WQMeterResponse, WQMeterSensorRecordsResponse
from app.features.meters.infrastructure.repo_meter_impl import WaterQualityMeterRepositoryImpl
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.share.jwt.domain.payload import MeterPayload
from app.share.jwt.infrastructure.access_token import AccessToken
from app.share.users.infra.users_repo_impl import UserRepositoryImpl
from app.share.workspace.workspace_access import WorkspaceAccess
from app.share.weatherapi.domain.model import CurrentWeatherResponse, HistoricalWeatherResponse
from app.share.weatherapi.services.services import WeatherService

meters_router = APIRouter(
    prefix="/meters",
    tags=["Meters"]
)


access_token_connection = AccessToken[MeterPayload]()

workspace_access = WorkspaceAccess()
user_repo = UserRepositoryImpl()

water_quality_meter_repo = WaterQualityMeterRepositoryImpl(
    access=workspace_access)
meter_connection = WaterQMConnectionImpl(
    meter_repo=water_quality_meter_repo)
meter_records_repo = MeterRecordsRepositoryImpl(
    workspace_access=WorkspaceAccess())
weather_service = WeatherService()


@meters_router.get("/{id_workspace}/")
async def all(id_workspace: str, user=Depends(verify_access_token)) -> WQMeterGetResponse:
    try:
        data = water_quality_meter_repo.get_list(id_workspace, user.uid)
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
            id_workspace, user.uid, meter)
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
            id_workspace=id_workspace, owner=user.uid, id_meter=id_meter, meter=meter)
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
            id_workspace=id_workspace, owner=user.uid, id_meter=id_meter)
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
async def delete(id_workspace: str, id_meter: str, user=Depends(verify_access_token)) -> WQMeterResponse:
    try:
        meter = water_quality_meter_repo.delete(
            id_workspace=id_workspace, owner=user.uid, id_meter=id_meter)
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
async def connect(id_workspace: str,  id_meter: str, user=Depends(verify_access_token)) -> WQMeterPasswordResponse:
    try:
        password = meter_connection.create(
            id_workspace, user.uid, id_meter)
        return WQMeterPasswordResponse(
            message="Password created successfully",
            password=password
        )
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@meters_router.get("/receive/{password}/")
async def connect(password: int) -> WQMeterConnectResponse:
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

        return WQMeterConnectResponse(
            message="Connection received",
            token=token
        )
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@meters_router.get("/{id_workspace}/weather/{id_meter}/")
async def get_weather(
    id_workspace: str,
    id_meter: str,
    last_days: int = None,
    user=Depends(verify_access_token)
) -> CurrentWeatherResponse | HistoricalWeatherResponse:
    try:
        # Obtener el medidor con validación de dueño
        meter = water_quality_meter_repo.get(
            id_workspace=id_workspace,
            owner=user.uid,
            id_meter=id_meter
        )
        print("🚰 Meter obtenido:", meter)
        print("📍 Ubicación:", meter.location)

        if not meter or not meter.location:
            raise HTTPException(
                status_code=404, detail="Medidor no encontrado o sin coordenadas")

        # Obtener clima según la ubicación del medidor
        if last_days:
            response = await weather_service.get_historical_weather(
                meter.location.lat,
                meter.location.lon,
                last_days
            )
            print("🌤️ Clima histórico:", response)
        else:
            response = await weather_service.get_current_weather(
                meter.location.lat,
                meter.location.lon
            )

        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)

        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Error del servidor")


@meters_router.get("/{id_workspace}/{id_meter}/")
async def get_records_meter(id_workspace: str, id_meter: str, user=Depends(verify_access_token)) -> WQMeterRecordsResponse:
    try:
        identifier = SensorIdentifier(
            meter_id=id_meter, workspace_id=id_workspace, user_id=user.uid)
        params = SensorQueryParams()
        meter_records = meter_records_repo.get_latest_sensor_records(
            identifier, params)
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
                             descending: bool = True, convert_timestamp: bool = False, user=Depends(verify_access_token)) -> WQMeterSensorRecordsResponse:
    try:
        identifier = SensorIdentifier(
            meter_id=id_meter, workspace_id=id_workspace, user_id=user.uid, sensor_name=sensor_name)
        params = SensorQueryParams(
            limit=limit, descending=descending, convert_timestamp=convert_timestamp)
        sensor_records = meter_records_repo.get_sensor_records(
            identifier, params)
        return WQMeterSensorRecordsResponse(message="Records retrieved successfully", records=sensor_records)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
