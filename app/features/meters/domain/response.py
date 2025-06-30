from app.features.meters.domain.model import SensorRecordsResponse, WaterQualityMeter
from app.share.response.model import ResponseApi
from app.share.socketio.domain.model import Record


class WQMeterResponse(ResponseApi):
    meter: WaterQualityMeter


class WQMeterGetResponse(ResponseApi):
    meters: list[WaterQualityMeter]


class WQMeterRecordsResponse(ResponseApi):
    records: SensorRecordsResponse


class WQMeterSensorRecordsResponse(ResponseApi):
    records: list[Record]


class WQMeterPasswordResponse(ResponseApi):
    password: int


class WQMeterConnectResponse(ResponseApi):
    token: str
