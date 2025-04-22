from app.features.alerts.domain.model import Alert
from app.share.response.model import ResponseApi


class ResponseAlert(ResponseApi):
    alert: Alert


class ResponseAlerts(ResponseApi):
    alerts: list[Alert]
