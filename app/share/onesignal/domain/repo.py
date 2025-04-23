from abc import ABC, abstractmethod

from app.share.onesignal.domain.model import Notification


class SenderServiceRepository(ABC):
    @abstractmethod
    def send_notification(self, notification: Notification) -> dict:
        pass
