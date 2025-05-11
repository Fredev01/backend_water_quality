import time
from firebase_admin import db
from app.share.messages.domain.model import NotificationBody, NotificationControl
from app.share.messages.domain.repo import NotificationManagerRepository


class NotificationManagerRepositoryImpl(NotificationManagerRepository):
    """
    Implementation of the NotificationManagerRepository interface.
    This class is responsible for managing notifications.
    """

    def create(self, notification: NotificationBody) -> NotificationBody:
        ref = db.reference("/notifications_history/")

        result = ref.push(notification.model_dump())

        notification.id = result.key

        return notification

    def mark_as_read(self, notification_id: str) -> NotificationBody:

        notification_ref = db.reference(
            f"/notifications_history/{notification_id}/")

        notification_data = notification_ref.get(shallow=True)

        if notification_data is None:
            raise ValueError(
                f"Notification with ID {notification_id} not found.")

        notification_ref.update({"read": True})

        notification = NotificationBody(**notification_data)
        notification.id = notification_id
        notification.read = True
        return notification

    def get_history(self, user_uid: str) -> list[NotificationBody]:

        notifications_ref = db.reference(
            f"/notifications_history/").order_by_child("user_id").equal_to(user_uid)

        notifications_data = notifications_ref.get()
        if notifications_data is None:
            return []

        notifications = []

        for notification_id, notification_data in notifications_data.items():

            notification = NotificationBody(**notification_data)
            notification.id = notification_id
            notifications.append(notification)

        return notifications

    def create_control(self, alert: NotificationControl) -> NotificationControl:
        print("Creating control for alert:", alert.alert_id)
        db.reference(
            f"/notifications_control/{alert.alert_id}/").set(alert.model_dump())
        return alert

    def get_control(self, alert_id: str) -> NotificationControl:
        print("Getting control for alert:", alert_id)

        notification_ref = db.reference(
            f"/notifications_control/{alert_id}/")

        notification_data = notification_ref.get()
        print("Notification data:", notification_data)
        if notification_data is None:
            print("Control not found, creating new one")
            return self.create_control(NotificationControl(
                alert_id=alert_id,
                validation_count=0,
            ))

        notification = NotificationControl(**notification_data)

        return notification

    def update_control_validation(self, alert_id: str):
        ref = db.reference(
            f'/notifications_control/{alert_id}/validation_count')
        current_count = ref.get() or 0
        ref.set(current_count + 1)

    def reset_control_validation(self, alert_id: str):
        # Logic to reset control validation for an alert
        ref = db.reference(
            f'/notifications_control/{alert_id}/validation_count')

        if ref.get() is None:
            return

        ref.set(0)

    def update_control_last_sent(self, alert_id: str, last_sent: float):
        # Logic to update the last sent timestamp for an alert
        ref = db.reference(
            f'/notifications_control/{alert_id}/last_sent')

        ref.set(last_sent)
