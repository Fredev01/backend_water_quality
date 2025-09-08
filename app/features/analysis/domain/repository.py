from abc import ABC, abstractmethod

from app.features.analysis.domain.enums import AnalysisEnum

from app.features.analysis.domain.models.average import AveragePeriod, AverageRange
from app.features.analysis.domain.models.correlation import CorrelationParams
from app.features.analysis.domain.models.prediction import PredictionParam
from app.share.meter_records.domain.model import SensorIdentifier


class AnalysisAverageRepository(ABC):
    @abstractmethod
    def get_analysis(self, identifier: SensorIdentifier, analysis_type: AnalysisEnum):
        pass

    @abstractmethod
    def create_average(self, identifier: SensorIdentifier, average_range: AverageRange):
        pass

    @abstractmethod
    def create_average_period(
        self, identifier: SensorIdentifier, average_period: AveragePeriod
    ):
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
