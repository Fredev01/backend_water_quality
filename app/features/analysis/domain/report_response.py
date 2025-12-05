from app.share.response.model import ResponseApi


class AnalysisReportResponse(ResponseApi):
    """Response model for PDF report generation endpoint"""

    filename: str
    size_bytes: int
