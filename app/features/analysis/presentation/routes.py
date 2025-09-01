from fastapi import APIRouter, Depends, HTTPException
from app.features.analysis.domain.model import AverageIdentifier, AverageRange
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
    identifier: AverageIdentifier,
    range: AverageRange,
    user: UserPayload = Depends(verify_access_token),
    analysis_avarage: AnalysisAvarageRepository = Depends(get_analysis_avarage),
):

    try:
        result = analysis_avarage.create_avarage(
            identifier=SensorIdentifier(
                workspace_id=identifier.workspace_id,
                meter_id=identifier.meter_id,
                user_id=user.uid,
                sensor_name=identifier.sensor_name,
            ),
            avarage_range=range,
        )
        return result

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
