import uuid
from datetime import datetime
from typing import Any

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
    ):
        self.access = access
        self.analysis_repo: AnalysisRepository = analysis_repo
        self.collection = "analysis"

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

    def delete_analysis(self, user_id: str, analysis_id: str) -> None:

        analysis_ref = self._get_analysis_ref(analysis_id)

        identifier = SensorIdentifier(
            workspace_id=analysis_ref.child("workspace_id").get(),
            meter_id=analysis_ref.child("meter_id").get(),
            user_id=user_id,
        )

        self._check_access(identifier)

        analysis_ref.delete()

    def _time_now(self):
        return str(datetime.now())

    def create_analysis(
        self,
        identifier: SensorIdentifier,
        analysis_type: AnalysisEnum,
        parameters: dict,
    ) -> str:

        work_ref = self._check_access(identifier)

        # Create analysis document with initial status
        analysis_id = str(uuid.uuid4())
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

        # Save initial document
        self._get_analysis_ref(analysis_id).set(analysis_data)

        email_list: list = []

        if work_ref.user:
            email_list.append(work_ref.user.email)
        if work_ref.owner:
            email_list.append(work_ref.owner.email)

        # Start background task to generate analysis
        self._generate_analysis(
            identifier,
            analysis_type,
            analysis_id,
            parameters,
            email_list=email_list,
        )

        return analysis_id

    def _generate_analysis(
        self,
        identifier,
        analysis_type,
        analysis_id,
        params,
        email_list: list,
        is_update=False,
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
                }
            )

            print(params)

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
    ) -> None:

        analysis_ref = self._get_analysis_ref(analysis_id)
        workspace_id = analysis_ref.child("workspace_id").get()
        meter_id = analysis_ref.child("meter_id").get()

        if workspace_id is None or meter_id is None:
            print("Not foundo")
            return

        identifier = SensorIdentifier(
            workspace_id=workspace_id,
            meter_id=meter_id,
            user_id=user_id,
        )

        work_ref = self._check_access(identifier)

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

        email_list: list = []

        if work_ref.user:
            email_list.append(work_ref.user.email)
        if work_ref.owner:
            email_list.append(work_ref.owner.email)

        if analysis_type:
            analysis_ref.update(
                {
                    "status": AnalysisStatus.UPDATING.value,
                }
            )
            self._generate_analysis(
                identifier=identifier,
                analysis_id=analysis_id,
                params=parameters,
                analysis_type=analysis_type,
                email_list=email_list,
            )
