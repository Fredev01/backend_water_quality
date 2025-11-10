from functools import lru_cache
from fastapi import BackgroundTasks, Depends
from typing_extensions import Annotated


from app.features.analysis.infrastructure.firebase_analysis_result import (
    FirebaseAnalysisResultRepository,
)
from app.share.depends import (
    get_meter_records_repo,
    get_workspace_access,
)
from app.share.meter_records.domain.repository import MeterRecordsRepository

from app.features.analysis.infrastructure.analysis_impl import AnalysisAverage
from app.features.analysis.domain.repository import (
    AnalysisRepository,
    AnalysisResultRepository,
)
from app.share.workspace.workspace_access import WorkspaceAccess
from app.features.analysis.domain.chart_repository import AnalysisChartGenerator
from app.features.analysis.infrastructure.matplotlib_chart_generator import (
    MatplotlibAnalysisChartGenerator,
)
from app.share.reports.domain.repository import PDFReportGenerator
from app.share.reports.infrastructure.fpdf_generator import FPDF2ReportGenerator


@lru_cache
def get_analysis(
    record_repo: Annotated[MeterRecordsRepository, Depends(get_meter_records_repo)],
) -> AnalysisRepository:
    return AnalysisAverage(record_repo=record_repo)


@lru_cache
def get_analysis_result(
    access: Annotated[WorkspaceAccess, Depends(get_workspace_access)],
    analysis_rep: Annotated[AnalysisRepository, Depends(get_analysis)],
    background_tasks: BackgroundTasks,
) -> AnalysisResultRepository:
    return FirebaseAnalysisResultRepository(
        access=access, analysis_repo=analysis_rep, background_tasks=background_tasks
    )


@lru_cache
def get_analysis_chart_generator() -> AnalysisChartGenerator:
    """Get singleton instance of analysis chart generator"""
    return MatplotlibAnalysisChartGenerator()


@lru_cache
def get_pdf_generator() -> PDFReportGenerator:
    """Get singleton instance of PDF report generator"""
    return FPDF2ReportGenerator()
