from functools import lru_cache
from fastapi import Depends
from typing_extensions import Annotated


from app.share.depends import get_meter_records_repo
from app.share.meter_records.domain.repository import MeterRecordsRepository

from app.features.analysis.infrastructure.analysis_avarage import AnalysisAvarage
from app.features.analysis.domain.repository import AnalysisAvarageRepository


@lru_cache
def get_analysis_avarage(
    record_repo: Annotated[MeterRecordsRepository, Depends(get_meter_records_repo)],
) -> AnalysisAvarageRepository:
    return AnalysisAvarage(record_repo=record_repo)
