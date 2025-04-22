
from app.features.alerts.domain.model import Alert, AlertCreate, AlertQueryParams, AlertCreate, AlertUpdate
from app.features.alerts.domain.repo import AlertRepository


class AlertRepositoryImpl(AlertRepository):
    def create(self, owner: str, alert: AlertCreate) -> Alert:
        return Alert(
            id="1",
            title=alert.title,
            type=alert.type,
            workspace_id=alert.workspace_id,
            meter_id=alert.meter_id,
            owner=owner
        )

    def get(self, owner: str, alert_id: str) -> Alert | None:
        return Alert(
            id="1",
            title="Alert title",
            type="poor",
            workspace_id="1",
            meter_id="1",
            owner=owner
        )

    def query(self, owner: str, params: AlertQueryParams) -> list[Alert]:
        return [
            Alert(
                id="1",
                title="Alert title",
                type="poor",
                workspace_id="1",
                meter_id="1",
                owner=owner
            )
        ]

    def update(self, owner: str, alert_id: str, alert: AlertUpdate) -> Alert | None:
        return Alert(
            id=alert_id,
            title=alert.title,
            type=alert.type,
            workspace_id="1",
            meter_id="1",
            owner=owner
        )

    def delete(self, owner: str, alert_id: str) -> Alert:
        return Alert(
            id="1",
            title="Alert title",
            type="poor",
            workspace_id="1",
            meter_id="1",
            owner=owner
        )
