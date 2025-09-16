from fastapi import HTTPException
from firebase_admin import db
from datetime import datetime
from app.features.alerts.domain.model import (
    Alert,
    AlertCreate,
    AlertData,
    AlertQueryParams,
    AlertCreate,
    AlertUpdate,
)
from app.features.alerts.domain.repo import AlertRepository
from app.share.workspace.domain.model import WorkspaceRoles
from app.share.workspace.workspace_access import WorkspaceAccess


class AlertRepositoryImpl(AlertRepository):
    def __init__(self, access: WorkspaceAccess):
        self.access = access

    def is_meter_access(self, user: str, workspace_id: str, meter_id: str) -> bool:

        workspace_ref = self.access.get_ref(
            workspace_id,
            user,
            roles=[WorkspaceRoles.ADMINISTRATOR, WorkspaceRoles.MANAGER],
        )

        meter_ref = workspace_ref.ref.child("meters").child(meter_id)

        if meter_ref.get() is None:
            return False

        return True

    def create(self, owner: str, alert: AlertCreate) -> Alert:

        new_alert = AlertData(
            title=alert.title,
            type=alert.type,
            workspace_id=alert.workspace_id,
            meter_id=alert.meter_id,
            owner=owner,
            parameters=alert.parameters,
        )

        alert_ref = db.reference("/alerts").push(new_alert.model_dump())

        return Alert(
            id=alert_ref.key,
            title=alert.title,
            type=alert.type,
            workspace_id=alert.workspace_id,
            meter_id=alert.meter_id,
            owner=owner,
            parameters=alert.parameters,
        )

    def _get_if_owner(
        self,
        owner: str,
        alert_id: str,
        get_alert: bool = False,
        get_ref_alert: bool = False,
    ) -> db.Reference | Alert | tuple[db.Reference, Alert]:

        alert_ref = db.reference("/alerts").child(alert_id)
        alert = alert_ref.get()

        if alert is None:
            raise HTTPException(status_code=404, detail="Alert not found")

        if alert.get("owner") != owner:
            raise HTTPException(
                status_code=403, detail="No has access to the alert")

        if get_alert:
            return Alert(
                id=alert_id,
                title=alert.get("title"),
                type=alert.get("type"),
                workspace_id=alert.get("workspace_id"),
                meter_id=alert.get("meter_id"),
                owner=alert.get("owner"),
                parameters=alert.get("parameters") or {},
            )

        if get_ref_alert:
            return alert_ref, Alert(
                id=alert_id,
                title=alert.get("title"),
                type=alert.get("type"),
                workspace_id=alert.get("workspace_id"),
                meter_id=alert.get("meter_id"),
                owner=alert.get("owner"),
                parameters=alert.get("parameters") or {},
            )

        return alert_ref

    def get(self, owner: str, alert_id: str) -> Alert:

        return self._get_if_owner(owner, alert_id, get_alert=True)

    def query(self, owner: str, params: AlertQueryParams) -> list[Alert]:

        alerts_query = (
            db.reference(
                "/alerts").order_by_child("owner").equal_to(owner).get() or {}
        )

        alerts: list[Alert] = []

        for alert_id, alert_data in alerts_query.items():

            if (
                params.workspace_id is not None
                and alert_data.get("workspace_id") != params.workspace_id
            ):
                continue

            if (
                params.meter_id is not None
                and alert_data.get("meter_id") != params.meter_id
            ):
                continue

            if params.type is not None and alert_data.get("type") != params.type:
                continue

            alert = Alert(
                id=alert_id,
                title=alert_data.get("title"),
                type=alert_data.get("type"),
                workspace_id=alert_data.get("workspace_id"),
                meter_id=alert_data.get("meter_id"),
                owner=alert_data.get("owner"),
                parameters=alert_data.get("parameters") or {},
            )

            alerts.append(alert)

        return alerts

    def update(self, owner: str, alert_id: str, alert: AlertUpdate) -> Alert:

        alert_ref, alert_data = self._get_if_owner(
            owner, alert_id, get_ref_alert=True)

        alert_ref.update(alert.model_dump())

        return Alert(
            id=alert_id,
            title=alert.title,
            type=alert.type,
            workspace_id=alert_data.workspace_id,
            meter_id=alert_data.meter_id,
            owner=alert_data.owner,
            parameters=alert_data.parameters,
        )

    def delete(self, owner: str, alert_id: str) -> Alert:

        alert_ref, alert = self._get_if_owner(
            owner, alert_id, get_ref_alert=True)

        alert_ref.delete()

        return alert
