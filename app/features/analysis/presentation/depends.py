from functools import lru_cache
from fastapi import Depends
from typing_extensions import Annotated


from app.share.depends import get_meter_records_repo, get_workspace_access
from app.share.meter_records.domain.repository import MeterRecordsRepository

from app.features.analysis.infrastructure.analysis_average import AnalysisAverage
from app.features.analysis.domain.repository import AnalysisAverageRepository
from app.share.workspace.workspace_access import WorkspaceAccess


@lru_cache
def get_analysis_average(
    workspace_access: Annotated[WorkspaceAccess, Depends(get_workspace_access)],
    record_repo: Annotated[MeterRecordsRepository, Depends(get_meter_records_repo)],
) -> AnalysisAverageRepository:
    return AnalysisAverage(access=workspace_access, record_repo=record_repo)
