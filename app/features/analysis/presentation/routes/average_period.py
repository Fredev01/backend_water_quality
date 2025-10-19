from fastapi import APIRouter, Depends, HTTPException

from app.features.analysis.domain.enums import AnalysisEnum
from app.features.analysis.domain.models.average import AvgPeriodParam
from app.features.analysis.domain.models.correlation import AnalysisIdentifier
from app.features.analysis.domain.repository import AnalysisResultRepository
from app.features.analysis.presentation.depends import get_analysis_result
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.share.meter_records.domain.model import SensorIdentifier

average_period_router = APIRouter()


@average_period_router.get("/{work_id}/{meter_id}/")
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


@average_period_router.post("/")
async def create_average_period(
    identifier: AnalysisIdentifier,
    period: AvgPeriodParam,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):
    try:
        id = analysis_result.create_analysis(
            identifier=SensorIdentifier(
                workspace_id=identifier.workspace_id,
                meter_id=identifier.meter_id,
                user_id=user.uid,
                sensor_name=identifier.sensor_name,
            ),
            analysis_type=AnalysisEnum.AVERAGE_PERIOD,
            parameters=period.model_dump(),
        )

        if id is None:
            raise HTTPException(status_code=409, detail="El análisis ya existe")

        return {"message": f"Análisis generando con el id: {id}"}
    except HTTPException as he:
        raise he
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@average_period_router.put("/{id}/")
async def update_average_period(
    id: str,
    period: AvgPeriodParam,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
):
    try:
        analysis_id = analysis_result.update_analysis(
            user_id=user.uid,
            analysis_id=id,
            parameters=period.model_dump(),
        )

        if analysis_id is None:
            raise HTTPException(
                status_code=404, detail="No se pudo actualizar el análisis"
            )

        return {"message": f"Análisis con el id {analysis_id} actualizando"}
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
