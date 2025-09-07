from abc import ABC, abstractmethod

from app.features.analysis.domain.enums import AnalysisEnum
from app.features.analysis.domain.model import (
    AveragePeriod,
    AverageRange,
    AverageResult,
    AvgPeriodAllResult,
    AvgPeriodResult,
    CorrelationParams,
    PredictionParam,
)
from app.share.meter_records.domain.model import SensorIdentifier


class AnalysisAverageRepository(ABC):
    @abstractmethod
    def get_analysis(
        self, identifier: SensorIdentifier, analysis_type: AnalysisEnum
    ) -> AverageResult:
        pass

    @abstractmethod
    def create_average(
        self, identifier: SensorIdentifier, average_range: AverageRange
    ) -> AverageResult | list[AverageResult]:
        pass

    @abstractmethod
    def create_average_period(
        self, identifier: SensorIdentifier, average_period: AveragePeriod
    ) -> AvgPeriodAllResult | AvgPeriodResult:
        pass

    @abstractmethod
    def generate_prediction(
        self, identifier: SensorIdentifier, prediction_param: PredictionParam
    ):
        pass

    @abstractmethod
    def generate_correlation(
        self,
        identifier: SensorIdentifier,
        correlation_params: CorrelationParams,
    ):
        pass
