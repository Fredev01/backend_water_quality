from fastapi import APIRouter, Depends, HTTPException
from app.features.analysis.domain.enums import AnalysisEnum
from app.features.analysis.domain.model import (
    AverageIdentifier,
    AveragePeriod,
    AverageRange,
    CorrelationParams,
    PredictionParam,
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


@analysis_router.get("/average/{work_id}/{meter_id}/")
def get_average(
    work_id: str,
    meter_id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_average: AnalysisAverageRepository = Depends(get_analysis_average),
):

    try:
        result = analysis_average.get_analysis(
            identifier=SensorIdentifier(
                workspace_id=work_id, meter_id=meter_id, user_id=user.uid
            ),
            analysis_type=AnalysisEnum.AVERAGE,
        )
        return {"message": "", "result": result}

    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


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


@analysis_router.get("/average/period/{work_id}/{meter_id}/")
def get_averege_period(
    work_id: str,
    meter_id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_average: AnalysisAverageRepository = Depends(get_analysis_average),
):

    try:
        result = analysis_average.get_analysis(
            identifier=SensorIdentifier(
                workspace_id=work_id, meter_id=meter_id, user_id=user.uid
            ),
            analysis_type=AnalysisEnum.AVERAGE_PERIOD,
        )
        return {"message": "", "result": result}

    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
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


@analysis_router.get("/prediction/{work_id}/{meter_id}/")
def get_prediction(
    work_id: str,
    meter_id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_average: AnalysisAverageRepository = Depends(get_analysis_average),
):

    try:
        result = analysis_average.get_analysis(
            identifier=SensorIdentifier(
                workspace_id=work_id, meter_id=meter_id, user_id=user.uid
            ),
            analysis_type=AnalysisEnum.PREDICTION,
        )
        return {"message": "", "result": result}

    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.post("/prediction/")
def create_prediction(
    identifier: AverageIdentifier,
    prediction_param: PredictionParam,
    user: UserPayload = Depends(verify_access_token),
    analysis_average: AnalysisAverageRepository = Depends(get_analysis_average),
):
    try:
        result = analysis_average.generate_prediction(
            identifier=SensorIdentifier(
                workspace_id=identifier.workspace_id,
                meter_id=identifier.meter_id,
                user_id=user.uid,
                sensor_name=identifier.sensor_name,
            ),
            prediction_param=prediction_param,
        )

        return result
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.get("/correlation/{work_id}/{meter_id}/")
def get_correlation(
    work_id: str,
    meter_id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_average: AnalysisAverageRepository = Depends(get_analysis_average),
):

    try:
        result = analysis_average.get_analysis(
            identifier=SensorIdentifier(
                workspace_id=work_id, meter_id=meter_id, user_id=user.uid
            ),
            analysis_type=AnalysisEnum.CORRELATION,
        )
        return {"message": "", "result": result}

    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.post("/correlation/")
def create_correlation(
    identifier: AverageIdentifier,
    correlation_params: CorrelationParams,
    user: UserPayload = Depends(verify_access_token),
    analysis_average: AnalysisAverageRepository = Depends(get_analysis_average),
):
    try:
        result = analysis_average.generate_correlation(
            identifier=SensorIdentifier(
                workspace_id=identifier.workspace_id,
                meter_id=identifier.meter_id,
                user_id=user.uid,
                sensor_name=identifier.sensor_name,
            ),
            correlation_params=correlation_params,
        )

        return result
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
