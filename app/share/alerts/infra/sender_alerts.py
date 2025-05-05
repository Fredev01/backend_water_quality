from firebase_admin import db
from app.share.alerts.domain.model import Alert, AlertValidated, NotificationBody
from app.share.alerts.domain.repo import SenderAlertsRepository, SenderServiceRepository
from app.share.socketio.domain.model import RecordBody


class SenderAlertsRepositoryImpl(SenderAlertsRepository):
    def __init__(self, sender_service: SenderServiceRepository):
        self.sender_service = sender_service

    def _list_alerts_by_meter(self, meter_id) -> list[Alert]:
        # Fetch alerts for the given meter_id from Firebase Realtime Database
        ref = db.reference().child("alerts").order_by_child("meter_id").equal_to(meter_id)

        alerts_data = ref.get()

        alerts = []

        for alert_id, alert in alerts_data.items():

            alerts.append(Alert(
                id=alert_id,
                meter_id=alert.get('meter_id'),
                title=alert.get('title'),
                type=alert.get('type'),
                validation_count=alert.get('validation_count'),
                notification_count=alert.get('notification_count'),
                user_uid=alert.get('owner')
            ))

        return alerts

    def _validate_records(self, meter_id, records: RecordBody) -> list[AlertValidated]:
        alerts = self._list_alerts_by_meter(meter_id)

        print(alerts)

        return []

    async def seen_alerts(self, meter_id: str, records: RecordBody):
        alert_valid = self._validate_records(meter_id, records=records)

        await self.sender_service.send_notification(NotificationBody(
            title="Alertas de conductividad",
            body="Se han detectado nuevos valores de conductividad",
            user_id="HjzZAfEfh5eCdO8JNA4A6y9gpZ32"
        ))
        print("Alerts enviados")

    def _update_validation_count(self, meter_id, count):
        # Update the validation count for the given meter_id in Firebase
        ref = db.reference(f'/alerts/{meter_id}/validation_count')
        current_count = ref.get() or 0
        ref.set(current_count + count)

    def _reset_validation_count(self, meter_id):
        # Reset the validation count for the given meter_id in Firebase
        ref = db.reference(f'/alerts/{meter_id}/validation_count')
        ref.set(0)

    def _update_notification_count(self, meter_id, count):
        # Update the notification count for the given meter_id in Firebase
        ref = db.reference(f'/alerts/{meter_id}/notification_count')
        current_count = ref.get() or 0
        ref.set(current_count + count)
