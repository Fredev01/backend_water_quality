from abc import ABC, abstractmethod

from app.share.alerts.domain.model import Alert, AlertValidated
from app.share.socketio.domain.model import RecordBody


class SenderAlertsRepository(ABC):
    """
    Abstract class for managing alerts queries and operations.
    """

    @abstractmethod
    def seen_alerts(self, meter_id: str, record: RecordBody) -> None:
        """
        Mark alerts as seen for a specific meter.
        :param meter_id: The ID of the meter.
        """
        pass
