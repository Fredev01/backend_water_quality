import hashlib
import uuid
from datetime import datetime
from typing import Any

from fastapi import BackgroundTasks
from firebase_admin import db

from app.features.analysis.domain.enums import AnalysisEnum, AnalysisStatus
from app.features.analysis.domain.models.average import AverageRange, AvgPeriodParam
from app.features.analysis.domain.models.correlation import CorrelationParams
from app.features.analysis.domain.models.prediction import PredictionParam
from app.features.analysis.domain.repository import (
    AnalysisRepository,
    AnalysisResultRepository,
)

from app.share.meter_records.domain.model import SensorIdentifier
from app.share.workspace.domain.model import WorkspaceRoles
from app.share.workspace.workspace_access import WorkspaceAccess


class FirebaseAnalysisResultRepository(AnalysisResultRepository):
    def __init__(
        self,
        access: WorkspaceAccess,
        analysis_repo: AnalysisRepository,
        background_tasks: BackgroundTasks,
    ):
        self.access = access
        self.analysis_repo: AnalysisRepository = analysis_repo
        self.collection = "analysis"
        self.background_tasks = background_tasks

    def _get_analysis_ref(self, analysis_id: str | None = None):
        ref = db.reference().child(self.collection)
        return ref.child(analysis_id) if analysis_id else ref

    def _check_access(self, identifier: SensorIdentifier):
        return self.access.get_ref(
            workspace_id=identifier.workspace_id,
            user=identifier.user_id,
            roles=[WorkspaceRoles.ADMINISTRATOR, WorkspaceRoles.MANAGER],
        )

    async def get_analysis(
        self,
        identifier: SensorIdentifier,
        analysis_type: AnalysisEnum,
        analysis_id: str | None = None,
    ) -> list | dict:
        self._check_access(identifier)

        analysis_ref = (
            self._get_analysis_ref(analysis_id)
            if analysis_id
            else self._get_analysis_ref()
        )

        if analysis_id:
            return analysis_ref.get()
        else:
            return (
                analysis_ref.order_by_child("type").equal_to(analysis_type.value).get()
            )

    def get_analysis_by_id(self, user_id: str, analysis_id: str) -> dict[str, Any] | None:
        """Get a specific analysis by ID"""
        analysis_ref = self._get_analysis_ref(analysis_id)
        analysis_data = analysis_ref.get()

        if not analysis_data:
            return None

        workspace_id = analysis_data.get("workspace_id")
        meter_id = analysis_data.get("meter_id")

        if workspace_id is None or meter_id is None:
            return None

        identifier = SensorIdentifier(
            workspace_id=workspace_id,
            meter_id=meter_id,
            user_id=user_id,
        )

        self._check_access(identifier)

        return analysis_data

    def delete_analysis(self, user_id: str, analysis_id: str) -> bool:

        analysis_ref = self._get_analysis_ref(analysis_id)

        workspace_id = analysis_ref.child("workspace_id").get()
        meter_id = analysis_ref.child("meter_id").get()

        if workspace_id is None or meter_id is None:
            print("Not foundo")
            return False

        identifier = SensorIdentifier(
            workspace_id=workspace_id,
            meter_id=meter_id,
            user_id=user_id,
        )

        self._check_access(identifier)

        analysis_ref.delete()
        return True

    def _time_now(self):
        return str(datetime.now())

    def _generate_id(
        self, identifier: SensorIdentifier, params: dict, analysis_type: str
    ) -> str:
        """
        Genera un uuid con el identificador y parametros de la predicción
        """

        start_date = params.get("start_date")
        end_date = params.get("end_date")

        analysis_id = f"{identifier.workspace_id}{identifier.meter_id}-{start_date}-{end_date}-{analysis_type}"

        sensor_type = params.get("sensor_type")
        if sensor_type is not None:
            analysis_id += f"-{sensor_type}"

        processed_params = {"start_date", "end_date", "sensor_type"}

        remaining_params = {
            k: v
            for k, v in params.items()
            if k not in processed_params and v is not None
        }

        for key in sorted(remaining_params.keys()):
            analysis_id += f"-{remaining_params[key]}"

        hash_obj = hashlib.sha256(analysis_id.replace(" ", "-").encode("utf-8"))
        hash_bytes = hash_obj.digest()[:16]

        analysis_uuid = str(uuid.UUID(bytes=hash_bytes))
        return analysis_uuid

    def create_analysis(
        self,
        identifier: SensorIdentifier,
        analysis_type: AnalysisEnum,
        parameters: dict,
    ) -> str | None:

        self._check_access(identifier)

        # Create analysis document with initial status

        analysis_id = self._generate_id(
            identifier=identifier, params=parameters, analysis_type=analysis_type.value
        )

        date = self._time_now()

        analysis_data = {
            "workspace_id": identifier.workspace_id,
            "meter_id": identifier.meter_id,
            "created_at": str(date),
            "updated_at": str(date),
            "status": AnalysisStatus.CREATING.value,
            "type": analysis_type.value,
            "parameters": parameters,
            "data": None,
        }

        ref = self._get_analysis_ref(analysis_id)

        if ref.get(etag=False) is not None:
            return None

        # Save initial document
        ref.set(analysis_data)

        # Start background task to generate analysis
        self.background_tasks.add_task(
            self._generate_analysis,
            identifier,
            analysis_type,
            analysis_id,
            parameters,
        )

        return analysis_id

    def _generate_analysis(
        self,
        identifier,
        analysis_type,
        analysis_id,
        params,
    ):
        """Background task to generate analysis data"""
        try:
            # Call the appropriate method based on analysis type
            if analysis_type == AnalysisEnum.AVERAGE:
                result = self.analysis_repo.generate_average(
                    identifier, average_range=AverageRange(**params)
                )
            elif analysis_type == AnalysisEnum.AVERAGE_PERIOD:
                result = self.analysis_repo.generate_average_period(
                    identifier, average_period=AvgPeriodParam(**params)
                )
            elif analysis_type == AnalysisEnum.PREDICTION:
                result = self.analysis_repo.generate_prediction(
                    identifier, PredictionParam(**params)
                )
            elif analysis_type == AnalysisEnum.CORRELATION:
                result = self.analysis_repo.generate_correlation(
                    identifier, CorrelationParams(**params)
                )
            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")

            # Update with results
            self._get_analysis_ref(analysis_id).update(
                {
                    "data": (result.model_dump(mode="json")),
                    "status": AnalysisStatus.SAVED.value,
                    "updated_at": self._time_now(),
                    "error": "",
                }
            )

        except Exception as e:
            # Update with error
            self._get_analysis_ref(analysis_id).update(
                {
                    "status": AnalysisStatus.ERROR.value,
                    "error": str(e),
                    "updated_at": self._time_now(),
                }
            )

    def update_analysis(
        self,
        user_id: str,
        analysis_id: str,
        parameters: dict[str, Any],
    ) -> str | None:

        analysis_ref = self._get_analysis_ref(analysis_id)
        workspace_id = analysis_ref.child("workspace_id").get()
        meter_id = analysis_ref.child("meter_id").get()

        if workspace_id is None or meter_id is None:
            print("Not foundo")
            return None

        identifier = SensorIdentifier(
            workspace_id=workspace_id,
            meter_id=meter_id,
            user_id=user_id,
        )

        self._check_access(identifier)

        analysis_type = None
        analysis_type_str = analysis_ref.child("type").get()

        if analysis_type_str == AnalysisEnum.AVERAGE.value:
            analysis_type = AnalysisEnum.AVERAGE
        elif analysis_type_str == AnalysisEnum.AVERAGE_PERIOD.value:
            analysis_type = AnalysisEnum.AVERAGE_PERIOD
        elif analysis_type_str == AnalysisEnum.CORRELATION.value:
            analysis_type = AnalysisEnum.CORRELATION
        elif analysis_type_str == AnalysisEnum.PREDICTION.value:
            analysis_type = AnalysisEnum.PREDICTION

        if analysis_id is None:
            return None

        analysis_ref.update(
            {
                "status": AnalysisStatus.UPDATING.value,
            }
        )

        self.background_tasks.add_task(
            self._generate_analysis,
            identifier=identifier,
            analysis_id=analysis_id,
            params=parameters,
            analysis_type=analysis_type,
        )

        return analysis_id
