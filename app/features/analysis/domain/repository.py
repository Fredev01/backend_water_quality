from abc import ABC, abstractmethod

from app.features.analysis.domain.model import AvarageRange
from app.share.meter_records.domain.model import (
    AvarageResult,
    SensorIdentifier,
)


class AnalysisAvarageRepository(ABC):
    @abstractmethod
    def get_analysis(
        self, identifier: SensorIdentifier, avarage_range: AvarageRange
    ) -> AvarageResult:
        pass

    @abstractmethod
    def create_avarage(
        self, identifier: SensorIdentifier, avarage_range: AvarageRange
    ) -> AvarageResult:
        pass
