from app.features.meters.domain.model import WaterQualityMeter
from app.share.meter_records.domain.response import SensorRecordsResponse
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


class WQMeterConnectResponse(ResponseApi):
    token: str
