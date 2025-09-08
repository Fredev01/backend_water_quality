from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.features.analysis.domain.enums import AnalysisEnum

from app.features.analysis.domain.models.average import AverageRange, AvgPeriodParam
from app.features.analysis.domain.models.correlation import (
    AnalysisIdentifier,
    CorrelationParams,
)
from app.features.analysis.domain.models.prediction import PredictionParam
from app.features.analysis.domain.repository import (
    AnalysisResultRepository,
)

from app.features.analysis.presentation.depends import get_analysis, get_analysis_result
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.share.meter_records.domain.model import SensorIdentifier

analysis_router = APIRouter(prefix="/analysis", tags=["analysis"])


@analysis_router.get("/average/{work_id}/{meter_id}/")
async def get_average(
    work_id: str,
    meter_id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):
    try:
        result = await analysis_result.get_analysis(
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
async def create_average(
    identifier: AnalysisIdentifier,
    range: AverageRange,
    background_tasks: BackgroundTasks,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):

    try:

        background_tasks.add_task(
            analysis_result.create_analysis,
            identifier=SensorIdentifier(
                workspace_id=identifier.workspace_id,
                meter_id=identifier.meter_id,
                user_id=user.uid,
                sensor_name=identifier.sensor_name,
            ),
            analysis_type=AnalysisEnum.AVERAGE,
            parameters=range.model_dump(),
        )

        return {"message": "Analisis generando, se enviara un correo cuando este listo"}

    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.put("/average/{id}/")
async def update_average(
    id: str,
    range: AverageRange,
    background_tasks: BackgroundTasks,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):

    try:

        background_tasks.add_task(
            analysis_result.update_analysis,
            user_id=user.uid,
            analysis_id=id,
            parameters=range.model_dump(),
        )

        return {
            "message": "Analisis actualizando, se enviara un correo cuando este listo"
        }

    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.get("/average/period/{work_id}/{meter_id}/")
async def get_averege_period(
    work_id: str,
    meter_id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):

    try:
        result = await analysis_result.get_analysis(
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
async def create_average_period(
    identifier: AnalysisIdentifier,
    period: AvgPeriodParam,
    background_tasks: BackgroundTasks,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):
    try:
        background_tasks.add_task(
            analysis_result.create_analysis,
            identifier=SensorIdentifier(
                workspace_id=identifier.workspace_id,
                meter_id=identifier.meter_id,
                user_id=user.uid,
                sensor_name=identifier.sensor_name,
            ),
            analysis_type=AnalysisEnum.AVERAGE_PERIOD,
            parameters=period.model_dump(),
        )

        return {"message": "Analisis generando, se enviara un correo cuando este listo"}
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.put("/average/period/{id}/")
async def update_average_period(
    id: str,
    period: AvgPeriodParam,
    background_tasks: BackgroundTasks,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):
    try:
        background_tasks.add_task(
            analysis_result.update_analysis,
            user_id=user.uid,
            analysis_id=id,
            parameters=period.model_dump(),
        )

        return {
            "message": "Analisis actualizando, se enviara un correo cuando este listo"
        }
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.get("/prediction/{work_id}/{meter_id}/")
async def get_prediction(
    work_id: str,
    meter_id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):

    try:
        result = await analysis_result.get_analysis(
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
async def create_prediction(
    identifier: AnalysisIdentifier,
    prediction_param: PredictionParam,
    background_tasks: BackgroundTasks,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):
    try:
        background_tasks.add_task(
            analysis_result.create_analysis,
            identifier=SensorIdentifier(
                workspace_id=identifier.workspace_id,
                meter_id=identifier.meter_id,
                user_id=user.uid,
                sensor_name=identifier.sensor_name,
            ),
            analysis_type=AnalysisEnum.PREDICTION,
            parameters=prediction_param.model_dump(),
        )

        return {"message": "Analisis generando, se enviara un correo cuando este listo"}
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.put("/prediction/{id}/")
async def update_prediction(
    id: str,
    prediction_param: PredictionParam,
    background_tasks: BackgroundTasks,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):
    try:
        background_tasks.add_task(
            analysis_result.update_analysis,
            user_id=user.uid,
            analysis_id=id,
            parameters=prediction_param.model_dump(),
        )

        return {
            "message": "Analisis actualizando, se enviara un correo cuando este listo"
        }
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.get("/correlation/{work_id}/{meter_id}/")
async def get_correlation(
    work_id: str,
    meter_id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):

    try:
        result = await analysis_result.get_analysis(
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
async def create_correlation(
    identifier: AnalysisIdentifier,
    correlation_params: CorrelationParams,
    background_tasks: BackgroundTasks,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):
    try:
        background_tasks.add_task(
            analysis_result.create_analysis,
            identifier=SensorIdentifier(
                workspace_id=identifier.workspace_id,
                meter_id=identifier.meter_id,
                user_id=user.uid,
                sensor_name=identifier.sensor_name,
            ),
            analysis_type=AnalysisEnum.CORRELATION,
            parameters=correlation_params.model_dump(),
        )

        return {"message": "Analisis generando, se enviara un correo cuando este listo"}
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.put("/correlation/{id}/")
async def update_correlation(
    id: str,
    correlation_params: CorrelationParams,
    background_tasks: BackgroundTasks,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):
    try:
        background_tasks.add_task(
            analysis_result.update_analysis,
            user_id=user.uid,
            analysis_id=id,
            parameters=correlation_params.model_dump(),
        )

        return {
            "message": "Analisis actualizando, se enviara un correo cuando este listo"
        }
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@analysis_router.delete("/{id}/")
async def delete_analysis(
    id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):
    try:
        analysis_result.delete_analysis(
            user_id=user.uid,
            analysis_id=id,
        )

        return {"message": "Analisis eliminado"}
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
