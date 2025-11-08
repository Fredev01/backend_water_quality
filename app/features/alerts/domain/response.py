from app.features.alerts.domain.model import Alert
from app.share.response.model import ResponseApi
from app.share.messages.domain.model import NotificationBody, NotificationBodyDatetime


class ResponseAlert(ResponseApi):
    alert: Alert


class ResponseAlerts(ResponseApi):
    alerts: list[Alert]


class NotificationsResponse(ResponseApi):
    notifications: list[NotificationBody | NotificationBodyDatetime]


class NotificationResponse(ResponseApi):
    notification: NotificationBody | NotificationBodyDatetime


class NotificationUpdateResponse(ResponseApi):
    notification: NotificationBody | NotificationBodyDatetime | None = None
