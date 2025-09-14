from fastapi import APIRouter, Depends, HTTPException
from app.features.alerts.domain.model import AlertCreate, AlertUpdate, AlertQueryParams
from app.features.alerts.domain.response import ResponseAlert, ResponseAlerts
from app.features.alerts.presentation.depends import (
    get_alerts_repo,
    get_notifications_history_repo,
)
from app.share.messages.domain.model import AlertType, QueryNotificationParams
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.share.messages.domain.repo import NotificationManagerRepository
from app.features.alerts.domain.repo import AlertRepository
from app.share.users.domain.model.user import UserData


alerts_router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
)


@alerts_router.get("/")
async def get_alerts(
    workspace_id: str = None,
    meter_id: str = None,
    type: AlertType = None,
    user=Depends(verify_access_token),
    alert_repo: AlertRepository = Depends(get_alerts_repo),
) -> ResponseAlerts:

    params = AlertQueryParams(workspace_id=workspace_id, meter_id=meter_id, type=type)

    alerts = alert_repo.query(owner=user.uid, params=params)

    return ResponseAlerts(message="Alerts retrieved successfully", alerts=alerts)


@alerts_router.get("/notifications/")
async def get_alerts_notifications(
    type: AlertType = None,
    is_read: bool = None,
    convert_timestamp: bool = False,
    user=Depends(verify_access_token),
    notifications_history_repo: NotificationManagerRepository = Depends(
        get_notifications_history_repo
    ),
):

    params = QueryNotificationParams(
        type=type, is_read=is_read, convert_timestamp=convert_timestamp
    )
    notifications = notifications_history_repo.get_history(
        user_uid=user.uid, params=params
    )

    return {
        "message": "Notifications retrieved successfully",
        "notifications": notifications,
    }


@alerts_router.put("/notifications/{notification_id}/")
async def mark_as_read(
    notification_id: str,
    user=Depends(verify_access_token),
    notifications_history_repo: NotificationManagerRepository = Depends(
        get_notifications_history_repo
    ),
):

    notification = notifications_history_repo.mark_as_read(notification_id)

    return {"message": "Notification marked as read", "notification": notification}


@alerts_router.get("/{id}/")
async def get_alert(
    id: str,
    user=Depends(verify_access_token),
    alert_repo: AlertRepository = Depends(get_alerts_repo),
) -> ResponseAlert:

    alert = alert_repo.get(owner=user.uid, alert_id=id)

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return ResponseAlert(message="Alert retrieved successfully", alert=alert)


@alerts_router.post("/")
async def create_alert(
    alert_body: AlertCreate,
    user: UserData = Depends(verify_access_token),
    alert_repo: AlertRepository = Depends(get_alerts_repo),
) -> ResponseAlert:

    is_access = alert_repo.is_meter_access(
        user.uid, alert_body.workspace_id, alert_body.meter_id
    )

    if not is_access:
        raise HTTPException(
            status_code=403, detail="Access needed to the meter or workspace"
        )

    alert = alert_repo.create(owner=user.uid, alert=alert_body)

    return ResponseAlert(message="Alert created successfully", alert=alert)


@alerts_router.put("/{id}/")
async def update_alert(
    id: str,
    alert_body: AlertUpdate,
    user=Depends(verify_access_token),
    alert_repo: AlertRepository = Depends(get_alerts_repo),
) -> ResponseAlert:
    alert = alert_repo.update(owner=user.uid, alert_id=id, alert=alert_body)

    return ResponseAlert(message="Alert updated successfully", alert=alert)


@alerts_router.delete("/{id}/")
async def delete_alert(
    id: str,
    user=Depends(verify_access_token),
    alert_repo: AlertRepository = Depends(get_alerts_repo),
) -> ResponseAlert:

    alert = alert_repo.delete(owner=user.uid, alert_id=id)

    return ResponseAlert(message="Alert deleted successfully", alert=alert)
