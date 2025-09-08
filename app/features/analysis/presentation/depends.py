from functools import lru_cache
from fastapi import Depends
from typing_extensions import Annotated


from app.features.analysis.infrastructure.firebase_analysis_result import (
    FirebaseAnalysisResultRepository,
)
from app.features.auth.presentation.depends import get_sender
from app.share.depends import (
    get_html_template,
    get_meter_records_repo,
    get_workspace_access,
)
from app.share.email.domain.repo import EmailRepository
from app.share.meter_records.domain.repository import MeterRecordsRepository

from app.features.analysis.infrastructure.analysis_impl import AnalysisAverage
from app.features.analysis.domain.repository import (
    AnalysisRepository,
    AnalysisResultRepository,
)
from app.share.workspace.workspace_access import WorkspaceAccess


@lru_cache
def get_analysis(
    record_repo: Annotated[MeterRecordsRepository, Depends(get_meter_records_repo)],
) -> AnalysisRepository:
    return AnalysisAverage(record_repo=record_repo)


@lru_cache
def get_analysis_result(
    access: Annotated[WorkspaceAccess, Depends(get_workspace_access)],
    sender: Annotated[EmailRepository, Depends(get_sender)],
    analysis_average: Annotated[AnalysisRepository, Depends(get_analysis)],
    html_template=Depends(get_html_template),
) -> AnalysisResultRepository:
    return FirebaseAnalysisResultRepository(
        access=access,
        analysis_average=analysis_average,
        sender=sender,
        html_template=html_template,
    )
