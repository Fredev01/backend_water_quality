from app.share.onesignal.domain.model import Notification
from app.share.onesignal.domain.repo import SenderServiceRepository


class OneSignalService(SenderServiceRepository):
    def send_notification(self, notification: Notification):
        print(notification)
        return {}
