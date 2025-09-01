from fastapi import APIRouter, Depends
from app.features.analysis.domain.model import AvarageIdentifier, AvarageRange
from app.features.analysis.domain.repository import AnalysisAvarageRepository

from app.features.analysis.presentation.depends import get_analysis_avarage
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.share.meter_records.domain.model import SensorIdentifier

analysis_router = APIRouter(prefix="/analysis", tags=["analysis"])


@analysis_router.get("/")
def get_analysis(user: UserPayload = Depends(verify_access_token)):
    return {"message": "Analysis endpoint"}


@analysis_router.post("/avarage/")
def create_avarage(
    identifier: AvarageIdentifier,
    range: AvarageRange,
    user: UserPayload = Depends(verify_access_token),
    analysis_avarage: AnalysisAvarageRepository = Depends(get_analysis_avarage),
):

    identifier = SensorIdentifier(
        workspace_id=identifier.workspace_id,
        meter_id=identifier.meter_id,
        user_id=user.uid,
    )

    result = analysis_avarage.create_avarage(identifier=identifier, avarage_range=range)

    return {"message": "Create avarage analysis", "result": result}
