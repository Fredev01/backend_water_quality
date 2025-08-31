from abc import ABC, abstractmethod


class AnalysisAvarageRepository(ABC):
    @abstractmethod
    def get_analysis(self, data: str) -> dict:
        pass

    @abstractmethod
    def create_avarage(self, data: str) -> dict:
        pass
