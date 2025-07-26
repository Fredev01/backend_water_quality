from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from app.features.meters.domain.repository import (
    MeterRecordsRepository,
    WaterQMConnection,
    WaterQualityMeterRepository,
)
from app.features.meters.infrastructure.meter_records_impl import (
    MeterRecordsRepositoryImpl,
)
from app.features.meters.infrastructure.repo_connect_impl import WaterQMConnectionImpl
from app.features.meters.infrastructure.repo_meter_impl import (
    WaterQualityMeterRepositoryImpl,
)
from app.share.depends import get_workspace_access
from app.share.jwt.domain.payload import MeterPayload
from app.share.jwt.infrastructure.access_token import AccessToken
from app.share.weatherapi.domain.repository import WeatherRepo
from app.share.weatherapi.services.services import WeatherService
from app.share.workspace.workspace_access import WorkspaceAccess


@lru_cache()
def get_access_token() -> AccessToken[MeterPayload]:
    return AccessToken[MeterPayload]()


@lru_cache()
def get_water_quality_meter_repo(
    workspace_access: Annotated[WorkspaceAccess, Depends(get_workspace_access)],
) -> WaterQualityMeterRepository:

    return WaterQualityMeterRepositoryImpl(access=workspace_access)


@lru_cache()
def get_meter_connection(
    water_quality_meter_repo: Annotated[
        WaterQualityMeterRepository, Depends(get_water_quality_meter_repo)
    ],
) -> WaterQMConnection:

    return WaterQMConnectionImpl(meter_repo=water_quality_meter_repo)


@lru_cache()
def get_meter_records_repo(
    workspace_access: Annotated[WorkspaceAccess, Depends(get_workspace_access)],
) -> MeterRecordsRepository:

    return MeterRecordsRepositoryImpl(workspace_access=workspace_access)


@lru_cache()
def get_weather_service() -> WeatherRepo:
    return WeatherService()
