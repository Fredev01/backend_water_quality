from fastapi import APIRouter, Depends, HTTPException
from app.features.analysis.domain.model import (
    AverageIdentifier,
    AveragePeriod,
    AverageRange,
)
from app.features.analysis.domain.repository import AnalysisAverageRepository

from app.features.analysis.presentation.depends import get_analysis_average
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.share.meter_records.domain.model import SensorIdentifier

analysis_router = APIRouter(prefix="/analysis", tags=["analysis"])


@analysis_router.get("/")
def get_analysis(user: UserPayload = Depends(verify_access_token)):
    return {"message": "Analysis endpoint"}


@analysis_router.post("/average/")
def create_average(
    identifier: AverageIdentifier,
    range: AverageRange,
    user: UserPayload = Depends(verify_access_token),
    analysis_average: AnalysisAverageRepository = Depends(get_analysis_average),
):

    try:
        result = analysis_average.create_average(
            identifier=SensorIdentifier(
                workspace_id=identifier.workspace_id,
                meter_id=identifier.meter_id,
                user_id=user.uid,
                sensor_name=identifier.sensor_name,
            ),
            average_range=range,
        )
        return result

    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.post("/average/period/")
def create_average_period(
    identifier: AverageIdentifier,
    period: AveragePeriod,
    user: UserPayload = Depends(verify_access_token),
    analysis_average: AnalysisAverageRepository = Depends(get_analysis_average),
):
    try:
        result = analysis_average.create_average_period(
            identifier=SensorIdentifier(
                workspace_id=identifier.workspace_id,
                meter_id=identifier.meter_id,
                user_id=user.uid,
                sensor_name=identifier.sensor_name,
            ),
            average_period=period,
        )

        return result
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
