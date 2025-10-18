from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any

from app.features.analysis.domain.enums import AnalysisEnum, AnalysisStatus
from app.features.analysis.domain.models.average import (
    AverageResult,
    AverageResultAll,
    AvgPeriodAllResult,
    AvgPeriodParam,
    AverageRange,
    AvgPeriodResult,
)
from app.features.analysis.domain.models.correlation import (
    CorrelationParams,
    CorrelationResult,
)
from app.features.analysis.domain.models.prediction import (
    PredictionParam,
    PredictionResult,
    PredictionResultAll,
)
from app.share.meter_records.domain.model import SensorIdentifier


T = TypeVar("T")


class AnalysisRepository(ABC):

    @abstractmethod
    def generate_average(
        self, identifier: SensorIdentifier, average_range: AverageRange
    ) -> AverageResult | AverageResultAll:
        pass

    @abstractmethod
    def generate_average_period(
        self, identifier: SensorIdentifier, average_period: AvgPeriodParam
    ) -> AvgPeriodAllResult | AvgPeriodResult:
        pass

    @abstractmethod
    def generate_prediction(
        self, identifier: SensorIdentifier, prediction_param: PredictionParam
    ) -> PredictionResult | PredictionResultAll:
        pass

    @abstractmethod
    def generate_correlation(
        self,
        identifier: SensorIdentifier,
        correlation_params: CorrelationParams,
    ) -> CorrelationResult:
        pass


class AnalysisResultRepository(ABC, Generic[T]):
    @abstractmethod
    def get_analysis(
        self,
        identifier: SensorIdentifier,
        analysis_type: AnalysisEnum,
        analysis_id: str | None = None,
    ) -> None:
        """
        Get analysis results by type and optional ID

        Args:
            identifier: Sensor identifier
            analysis_type: Type of analysis to retrieve
            analysis_id: Optional ID of a specific analysis

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_analysis_by_id(self, user_id: str, analysis_id: str) -> dict[str, Any] | None:
        """
        Get a specific analysis by ID

        Args:
            user_id: User ID requesting the analysis
            analysis_id: ID of the analysis to retrieve

        Returns:
            Analysis data or None if not found
        """
        pass

    @abstractmethod
    def create_analysis(
        self,
        identifier: SensorIdentifier,
        analysis_type: AnalysisEnum,
        parameters: dict[str, Any],
    ) -> str | None:
        """
        Create a new analysis

        Args:
            identifier: Sensor identifier
            analysis_type: Type of analysis being created
            data: Analysis result data
            parameters: Parameters used to generate the analysis

        Returns:
            ID of the created analysis
        """
        pass

    @abstractmethod
    def update_analysis(
        self,
        user_id: str,
        analysis_id: str,
        parameters: dict[str, Any],
    ) -> str | None:
        """
        Update an existing analysis

        Args:
            identifier: Sensor identifier
            analysis_id: ID of the analysis to update
            data: Updated analysis data
            status: New status of the analysis

        Returns:
            bool: True if update was successful
        """
        pass

    @abstractmethod
    def delete_analysis(self, user_id: str, analysis_id: str) -> bool:
        """
        Delete an analysis

        Args:
            identifier: Sensor identifier
            analysis_id: ID of the analysis to delete

        Returns:
            bool: True if deletion was successful
        """
        pass
