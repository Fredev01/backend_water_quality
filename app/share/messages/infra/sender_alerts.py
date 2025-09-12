from firebase_admin import db
import time
from datetime import datetime, timezone
from app.share.messages.domain.model import AlertData, NotificationControl,  NotificationBody, Parameter, RangeValue
from app.share.messages.domain.repo import NotificationManagerRepository, SenderAlertsRepository, SenderServiceRepository
from app.share.messages.domain.validate import RecordValidation
from app.share.socketio.domain.model import RecordBody


class SenderAlertsRepositoryImpl(SenderAlertsRepository):
    def __init__(self, sender_service: SenderServiceRepository, notification_manager: NotificationManagerRepository):
        self.sender_service = sender_service
        self.notification_manager = notification_manager

    def _list_alerts_by_meter(self, meter_id: str) -> list[AlertData]:
        # Fetch alerts for the given meter_id from Firebase Realtime Database
        ref = db.reference().child("alerts").order_by_child("meter_id").equal_to(meter_id)

        alerts_data = ref.get()

        alerts = []

        for alert_id, alert in alerts_data.items():
            parameters = alert.get('parameters') or {}
            parameters_transformed = []
            if parameters is not None:
                parameters_transformed = [
                    Parameter(**param) for param in parameters.values()]

            alerts.append(AlertData(
                id=alert_id,
                meter_id=alert.get('meter_id'),
                title=alert.get('title'),
                type=alert.get('type'),
                user_uid=alert.get('owner'),
                parameters=parameters_transformed
            ))

        return alerts

    def _validate_records(self, meter_id, records: RecordBody) -> list[AlertData]:
        alerts = self._list_alerts_by_meter(meter_id)

        if not alerts:
            print("Not found alerts for meter")
            return []

        levels_to_check = [alert.type for alert in alerts]
        parameters_and_ranges: dict[str, dict[str, RangeValue]] = {alert.type: {parameter.name: RangeValue(
            **parameter.ranges) for parameter in alert.parameters} for alert in alerts}

        alert_type = RecordValidation.validate(
            records, levels_to_check, parameters_and_ranges)

        if alert_type is None:
            alerts_ids = [alert.id for alert in alerts]

            for alert_id in alerts_ids:
                self.notification_manager.reset_control_validation(
                    alert_id=alert_id)

            print("Not found alert type")
            return []

        alerts_not_validated = [
            alert for alert in alerts if alert.type != alert_type]

        for alert in alerts_not_validated:
            self.notification_manager.reset_control_validation(
                alert_id=alert.id)

        alerts_validated = [
            alert for alert in alerts if alert.type == alert_type]

        return alerts_validated

    def _was_sent_today(self, last_sent: float | None) -> bool:
        if not last_sent:
            return False
        # Convert the timestamp to a datetime object
        last_date = datetime.fromtimestamp(last_sent, tz=timezone.utc).date()

        return last_date == datetime.now(timezone.utc).date()

    async def send_alerts(self, meter_id: str, records: RecordBody):
        alert_valid = self._validate_records(meter_id, records=records)

        if not alert_valid:
            print("Not found alerts for validation")
            return

        print(alert_valid)

        for alert in alert_valid:
            # Check if the alert is already validated

            notification_control = self.notification_manager.get_control(
                alert_id=alert.id)

            if notification_control.last_sent is not None and self._was_sent_today(notification_control.last_sent):
                continue

            if notification_control.validation_count < 5:
                self.notification_manager.update_control_validation(
                    alert_id=alert.id)
                continue

            # Send notification
            notification = NotificationBody(
                title=alert.title,
                body=f"Alert Type {alert.type.value.capitalize()} for meter {alert.meter_id}",
                user_id=alert.user_uid,
                timestamp=time.time()
            )

            await self.sender_service.send_notification(notification)

            # Update the notification count in Firebase
            self.notification_manager.update_control_last_sent(
                alert_id=alert.id, last_sent=notification.timestamp)
            self.notification_manager.reset_control_validation(
                alert_id=alert.id)

            self.notification_manager.update_control_last_sent(
                alert_id=alert.id, last_sent=notification.timestamp)

            self.notification_manager.create(notification)

            print(
                f"Notification sent to {alert.user_uid} for alert {alert.id}")
