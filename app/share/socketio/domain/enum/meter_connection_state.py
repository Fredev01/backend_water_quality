from enum import Enum


class MeterConnectionState(str, Enum):
    DISCONNECTED = "disconnected"  # The meter is disconnected
    CONNECTED = "connected"  # The meter is connected but not sending data
    SENDING_DATA = "sending_data"  # The meter is sending data
    ERROR = "error"  # The meter is sending data but there is an error
