from app.share.alerts.domain.model import Alert, AlertValidated
from app.share.alerts.domain.repo import SenderAlertsRepository
from firebase_admin import db

from app.share.onesignal.domain.model import Notification
from app.share.onesignal.domain.repo import SenderServiceRepository
from app.share.socketio.domain.model import RecordBody


class SenderAlertsService(SenderAlertsRepository):
    def __init__(self, sender_service: SenderServiceRepository):
        self.sender_service = sender_service

    def _list_alerts_by_meter(self, meter_id) -> list[Alert]:
        # Fetch alerts for the given meter_id from Firebase Realtime Database
        ref = db.reference().child("alerts").order_by_child("meter_id").equal_to(meter_id)

        print(ref.get())

        return []

    def _validate_records(self, meter_id, records: RecordBody) -> list[AlertValidated]:
        self._list_alerts_by_meter(meter_id)

        return []

    def seen_alerts(self, meter_id: str, records: RecordBody):
        self._validate_records(meter_id)

        self.sender_service.send_notification(Notification(
            title="Alertas de conductividad",
            body="Se han detectado nuevos valores de conductividad",
            user_id="123456789"
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
