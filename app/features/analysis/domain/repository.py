from abc import ABC, abstractmethod

from app.features.analysis.domain.model import AverageRange
from app.share.meter_records.domain.model import (
    AverageResult,
    SensorIdentifier,
)


class AnalysisAvarageRepository(ABC):
    @abstractmethod
    def get_analysis(
        self, identifier: SensorIdentifier, avarage_range: AverageRange
    ) -> AverageResult:
        pass

    @abstractmethod
    def create_avarage(
        self, identifier: SensorIdentifier, avarage_range: AverageRange
    ) -> AverageResult | list[AverageResult]:
        pass
