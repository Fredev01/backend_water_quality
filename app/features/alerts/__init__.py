from fastapi import APIRouter, Depends, HTTPException

from app.features.alerts.domain.model import AlertCreate, AlertUpdate, AlertQueryParams
from app.features.alerts.domain.response import ResponseAlert, ResponseAlerts
from app.features.alerts.infrastructure.repo_impl import AlertRepositoryImpl
from app.share.alerts.domain.model import AlertType
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.share.workspace.workspace_access import WorkspaceAccess


alerts_router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
)

workspace_access = WorkspaceAccess()
alert_repo = AlertRepositoryImpl(access=workspace_access)


@alerts_router.get("/")
async def get_alerts(workspace_id: str = None, meter_id: str = None, type: AlertType = None, user=Depends(verify_access_token)) -> ResponseAlerts:

    params = AlertQueryParams(
        workspace_id=workspace_id,
        meter_id=meter_id,
        type=type
    )

    alerts = alert_repo.query(owner=user.uid, params=params)

    return ResponseAlerts(
        message="Alerts retrieved successfully",
        alerts=alerts
    )


@alerts_router.get("/{id}/")
async def get_alert(id: str, user=Depends(verify_access_token)) -> ResponseAlert:

    alert = alert_repo.get(owner=user.uid, alert_id=id)

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return ResponseAlert(
        message="Alert retrieved successfully",
        alert=alert
    )


@alerts_router.post("/")
async def create_alert(alert_body: AlertCreate, user=Depends(verify_access_token)) -> ResponseAlert:

    is_access = alert_repo.is_meter_access(
        user.uid, alert_body.workspace_id, alert_body.meter_id)

    if not is_access:
        raise HTTPException(
            status_code=403, detail="Access needed to the meter or workspace")

    alert = alert_repo.create(owner=user.uid, alert=alert_body)

    return ResponseAlert(
        message="Alert created successfully",
        alert=alert
    )


@alerts_router.put("/{id}/")
async def update_alert(id: str, alert_body: AlertUpdate, user=Depends(verify_access_token)) -> ResponseAlert:
    alert = alert_repo.update(owner=user.uid, alert_id=id, alert=alert_body)

    return ResponseAlert(
        message="Alert updated successfully",
        alert=alert
    )


@alerts_router.delete("/{id}/")
async def delete_alert(id: str, user=Depends(verify_access_token)) -> ResponseAlert:

    alert = alert_repo.delete(owner=user.uid, alert_id=id)

    return ResponseAlert(
        message="Alert deleted successfully",
        alert=alert
    )
