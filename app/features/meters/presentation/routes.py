import time
from fastapi import APIRouter, Depends, HTTPException
from jwt import InvalidSignatureError
from app.features.meters.domain.model import (
    ValidMeterToken,
    WQMeterCreate,
    WQMeterUpdate,
    WQMeterCreate,
    WQMeterUpdate,
)
from app.features.meters.domain.repository import (
    WaterQualityMeterRepository,
)
from app.features.meters.domain.response import (
    WQMeterConnectResponse,
    WQMeterGetResponse,
    WQMeterRecordsResponse,
    WQMeterResponse,
    WQMeterSensorRecordsResponse,
)
from app.features.meters.presentation.depends import (
    get_access_token,
    get_meter_records_repo,
    get_water_quality_meter_repo,
    get_weather_service,
)
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.share.jwt.domain.payload import MeterPayload, UserPayload
from app.share.jwt.infrastructure.access_token import AccessToken
from app.share.meter_records.domain.model import SensorIdentifier, SensorQueryParams
from app.share.meter_records.domain.repository import MeterRecordsRepository
from app.share.response.model import ResponseApi
from app.share.weatherapi.domain.repository import WeatherRepo
from app.share.weatherapi.domain.model import (
    CurrentWeatherResponse,
    HistoricalWeatherResponse,
)

meters_router = APIRouter(prefix="/meters", tags=["Meters"])


@meters_router.get("/{id_workspace}/")
async def all(
    id_workspace: str,
    user=Depends(verify_access_token),
    water_quality_meter_repo: WaterQualityMeterRepository = Depends(
        get_water_quality_meter_repo
    ),
) -> WQMeterGetResponse:
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
async def create(
    id_workspace: str,
    meter: WQMeterCreate,
    user=Depends(verify_access_token),
    water_quality_meter_repo: WaterQualityMeterRepository = Depends(
        get_water_quality_meter_repo
    ),
) -> WQMeterResponse:
    try:

        new_meter = water_quality_meter_repo.add(id_workspace, user.uid, meter)
        return WQMeterResponse(message="Meter created successfully", meter=new_meter)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@meters_router.get("/{id_workspace}/{id_meter}/")
async def get(
    id_workspace: str,
    id_meter: str,
    user=Depends(verify_access_token),
    water_quality_meter_repo: WaterQualityMeterRepository = Depends(
        get_water_quality_meter_repo
    ),
) -> WQMeterResponse:
    try:
        meter = water_quality_meter_repo.get(
            id_workspace=id_workspace, owner=user.uid, id_meter=id_meter
        )
        return WQMeterResponse(message="Meter retrieved successfully", meter=meter)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@meters_router.put("/{id_workspace}/{id_meter}/")
async def update(
    id_workspace: str,
    id_meter: str,
    meter: WQMeterUpdate,
    user=Depends(verify_access_token),
    water_quality_meter_repo: WaterQualityMeterRepository = Depends(
        get_water_quality_meter_repo
    ),
) -> WQMeterResponse:
    try:
        meter_update = water_quality_meter_repo.update(
            id_workspace=id_workspace, owner=user.uid, id_meter=id_meter, meter=meter
        )
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
async def delete(
    id_workspace: str,
    id_meter: str,
    user=Depends(verify_access_token),
    water_quality_meter_repo: WaterQualityMeterRepository = Depends(
        get_water_quality_meter_repo
    ),
) -> WQMeterResponse:
    try:
        meter = water_quality_meter_repo.delete(
            id_workspace=id_workspace, owner=user.uid, id_meter=id_meter
        )
        return WQMeterResponse(message="Meter deleted successfully", meter=meter)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server Error")


@meters_router.post("/{id_workspace}/pair/{id_meter}/")
async def pair(
    id_workspace: str,
    id_meter: str,
    user: UserPayload = Depends(verify_access_token),
    access_token_connection: AccessToken[MeterPayload] = Depends(get_access_token),
    meter_repo: WaterQualityMeterRepository = Depends(get_water_quality_meter_repo),
) -> WQMeterConnectResponse:
    try:

        if meter_repo.is_active(id_workspace, user.uid, id_meter):
            raise HTTPException(status_code=409, detail="Medidor ya esta activo")

        payload = MeterPayload(
            id_workspace=id_workspace,
            owner=user.uid,
            id_meter=id_meter,
            exp=time.time() + 2592000,
        ).model_dump()

        token = access_token_connection.create(payload=payload)

        return WQMeterConnectResponse(message="Connection received", token=token)
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@meters_router.post("/{id_workspace}/pair/{id_meter}/validate/")
async def validate_pair(
    id_workspace: str,
    id_meter: str,
    valid_token: ValidMeterToken,
    user: UserPayload = Depends(verify_access_token),
    access_token_connection: AccessToken[MeterPayload] = Depends(get_access_token),
    meter_repo: WaterQualityMeterRepository = Depends(get_water_quality_meter_repo),
) -> ResponseApi:
    try:

        meter = meter_repo.get(id_workspace, user.uid, id_meter)

        decoded_token = access_token_connection.validate(valid_token.token)

        payload = MeterPayload(**decoded_token)

        if meter.id != payload.id_meter:
            raise HTTPException(
                status_code=403, detail="El token no es valido para este medidor"
            )

        return ResponseApi(message="Token valido")
    except HTTPException as he:
        raise he

    except InvalidSignatureError as ise:
        raise HTTPException(status_code=400, detail="Token invalido")
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@meters_router.get("/{id_workspace}/weather/{id_meter}/")
async def get_weather(
    id_workspace: str,
    id_meter: str,
    last_days: int = None,
    user=Depends(verify_access_token),
    water_quality_meter_repo: WaterQualityMeterRepository = Depends(
        get_water_quality_meter_repo
    ),
    weather_service: WeatherRepo = Depends(get_weather_service),
) -> CurrentWeatherResponse | HistoricalWeatherResponse:
    try:
        # Obtener el medidor con validación de dueño
        meter = water_quality_meter_repo.get(
            id_workspace=id_workspace, owner=user.uid, id_meter=id_meter
        )
        print("🚰 Meter obtenido:", meter)
        print("📍 Ubicación:", meter.location)

        if not meter or not meter.location:
            raise HTTPException(
                status_code=404, detail="Medidor no encontrado o sin coordenadas"
            )

        # Obtener clima según la ubicación del medidor
        if last_days:
            response = await weather_service.get_historical_weather(
                meter.location.lat, meter.location.lon, last_days
            )
            print("🌤️ Clima histórico:", response)
        else:
            response = await weather_service.get_current_weather(
                meter.location.lat, meter.location.lon
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


@meters_router.get("/records/{id_workspace}/{id_meter}/")
async def query_records(
    id_workspace: str,
    id_meter: str,
    start_date: str = None,
    end_date: str = None,
    sensor_type: str = None,
    limit: int = 10,
    index: str = None,
    user: UserPayload = Depends(verify_access_token),
    meter_records_repo: MeterRecordsRepository = Depends(get_meter_records_repo),
) -> WQMeterRecordsResponse:
    try:
        identifier = SensorIdentifier(
            meter_id=id_meter,
            workspace_id=id_workspace,
            user_id=user.uid,
        )
        params = SensorQueryParams(
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            sensor_type=sensor_type,
            index=index,
        )
        sensor_records = meter_records_repo.query_sensor_records(identifier, params)
        return WQMeterRecordsResponse(
            message="Records retrieved successfully", records=sensor_records
        )
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@meters_router.get("/records/{id_workspace}/{id_meter}/{sensor_name}/")
async def get_sensor_records(
    id_workspace: str,
    id_meter: str,
    sensor_name: str,
    limit: int = 10,
    index: str = None,
    user: UserPayload = Depends(verify_access_token),
    meter_records_repo: MeterRecordsRepository = Depends(get_meter_records_repo),
) -> WQMeterSensorRecordsResponse:
    try:
        identifier = SensorIdentifier(
            meter_id=id_meter,
            workspace_id=id_workspace,
            user_id=user.uid,
            sensor_name=sensor_name,
        )
        params = SensorQueryParams(
            limit=limit,
            index=index,
        )
        sensor_records = meter_records_repo.get_sensor_records(identifier, params)
        return WQMeterSensorRecordsResponse(
            message="Records retrieved successfully", records=sensor_records
        )
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=ve.args[0])
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
