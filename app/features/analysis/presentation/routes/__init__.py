from fastapi import APIRouter, Depends, HTTPException

from app.features.analysis.domain.repository import AnalysisResultRepository
from app.features.analysis.presentation.depends import get_analysis_result
from app.features.analysis.presentation.routes.average import average_router
from app.features.analysis.presentation.routes.average_period import (
    average_period_router,
)
from app.features.analysis.presentation.routes.correlation import correlation_router
from app.features.analysis.presentation.routes.prediction import prediction_router
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.verify_access_token import verify_access_token

analysis_router = APIRouter(prefix="/analysis", tags=["analysis"])

# Include subrouters for each analysis type
analysis_router.include_router(average_router, prefix="/average")
analysis_router.include_router(average_period_router, prefix="/average/period")
analysis_router.include_router(prediction_router, prefix="/prediction")
analysis_router.include_router(correlation_router, prefix="/correlation")


# Delete endpoint remains in the main router
@analysis_router.delete("/{id}/")
async def delete_analysis(
    id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):
    try:
        result = analysis_result.delete_analysis(
            user_id=user.uid,
            analysis_id=id,
        )

        if not result:
            raise HTTPException(status_code=404, detail="No existe el análisis")

        return {"message": "Análisis eliminado"}
    except HTTPException as he:
        print(he)
        raise he
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
