from typing import Any
from app.share.response.model import ResponseApi


class AnalysisResponse(ResponseApi):
    """Response model for GET analysis endpoints that return analysis results"""

    result: dict[str, Any]


class AnalysisCreateResponse(ResponseApi):
    """Response model for POST analysis endpoints that create new analysis"""

    pass


class AnalysisUpdateResponse(ResponseApi):
    """Response model for PUT analysis endpoints that update existing analysis"""

    pass


class AnalysisDeleteResponse(ResponseApi):
    """Response model for DELETE analysis endpoints that delete existing analysis"""

    pass
