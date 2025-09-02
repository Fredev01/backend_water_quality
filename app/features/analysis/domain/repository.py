from abc import ABC, abstractmethod

from app.features.analysis.domain.model import AveragePeriod, AverageRange
from app.share.meter_records.domain.model import (
    AverageResult,
    SensorIdentifier,
)


class AnalysisAverageRepository(ABC):
    @abstractmethod
    def get_analysis(
        self, identifier: SensorIdentifier, average_range: AverageRange
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
    ):
        pass
