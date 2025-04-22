from abc import ABC, abstractmethod

from app.features.alerts.domain.model import Alert, AlertCreate, AlertUpdate, AlertQueryParams


class AlertRepository(ABC):
    @abstractmethod
    def create(self, owner: str, alert: AlertCreate) -> Alert:
        pass

    @abstractmethod
    def get(self, owner: str, alert_id: str) -> Alert | None:
        pass

    @abstractmethod
    def query(self, owner: str, params: AlertQueryParams) -> list[Alert]:
        pass

    @abstractmethod
    def update(self, owner: str, alert_id: str, alert: AlertUpdate) -> Alert | None:
        pass

    @abstractmethod
    def delete(self, owner: str, alert_id: str) -> Alert:
        pass
