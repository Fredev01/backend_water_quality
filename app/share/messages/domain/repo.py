from abc import ABC, abstractmethod

from app.share.messages.domain.model import AlertData, NotificationBody
from app.share.socketio.domain.model import RecordBody


class SenderAlertsRepository(ABC):
    """
    Abstract class for managing alerts queries and operations.
    """

    @abstractmethod
    def send_alerts(self, meter_id: str, record: RecordBody) -> None:
        """
        Mark alerts as seen for a specific meter.
        :param meter_id: The ID of the meter.
        """
        pass


class SenderServiceRepository(ABC):
    @abstractmethod
    def send_notification(self, notification: NotificationBody) -> dict:
        pass
