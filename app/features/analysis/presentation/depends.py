from functools import lru_cache
from fastapi import Depends
from typing_extensions import Annotated


from app.share.depends import get_record_dataframe
from app.share.meter_records.domain.repository import RecordDataframeRepository

from app.features.analysis.infrastructure.analysis_average import AnalysisAverage
from app.features.analysis.domain.repository import AnalysisAverageRepository


@lru_cache
def get_analysis_average(
    record_dataframe: Annotated[
        RecordDataframeRepository, Depends(get_record_dataframe)
    ],
) -> AnalysisAverageRepository:
    return AnalysisAverage(record_dataframe=record_dataframe)
