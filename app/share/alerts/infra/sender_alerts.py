from firebase_admin import db
from app.share.alerts.domain.model import Alert,  NotificationBody
from app.share.alerts.domain.repo import SenderAlertsRepository, SenderServiceRepository
from app.share.alerts.domain.validate import RecordValidation
from app.share.socketio.domain.model import RecordBody


class SenderAlertsRepositoryImpl(SenderAlertsRepository):
    def __init__(self, sender_service: SenderServiceRepository):
        self.sender_service = sender_service

    def _list_alerts_by_meter(self, meter_id: str) -> list[Alert]:
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

    def _validate_records(self, meter_id, records: RecordBody) -> list[Alert]:
        alerts = self._list_alerts_by_meter(meter_id)

        if not alerts:
            print("Not found alerts for meter")
            return []

        levels_to_check = [alert.type for alert in alerts]

        alert_type = RecordValidation.validate(records, levels_to_check)

        if alert_type is None:
            print("Not found alert type")
            return []

        alerts_validated = [
            alert for alert in alerts if alert.type == alert_type]

        return alerts_validated

    async def seen_alerts(self, meter_id: str, records: RecordBody):
        alert_valid = self._validate_records(meter_id, records=records)

        if not alert_valid:
            print("Not found alerts for validation")
            return

        print(alert_valid)

        for alert in alert_valid:
            # Check if the alert is already validated
            if alert.validation_count <= 5:
                self._update_validation_count(alert.id)
                continue

            # Send notification
            notification = NotificationBody(
                title=alert.title,
                body=f"Alert Type {alert.type.value.capitalize()} for meter {alert.meter_id}",
                user_id=alert.user_uid
            )

            await self.sender_service.send_notification(notification)

            # Update the notification count in Firebase
            self._update_notification_count(alert.id)
            self._reset_validation_count(alert.id)
            print(
                f"Notification sent to {alert.user_uid} for alert {alert.id}")

    def _update_validation_count(self, id):
        # Update the validation count for the given meter_id in Firebase
        ref = db.reference(f'/alerts/{id}/validation_count')
        current_count = ref.get() or 0
        ref.set(current_count + 1)

    def _reset_validation_count(self, id):
        # Reset the validation count for the given meter_id in Firebase
        ref = db.reference(f'/alerts/{id}/validation_count')
        ref.set(0)

    def _update_notification_count(self, id):
        # Update the notification count for the given meter_id in Firebase
        ref = db.reference(f'/alerts/{id}/notification_count')
        current_count = ref.get() or 0
        ref.set(current_count + 1)
