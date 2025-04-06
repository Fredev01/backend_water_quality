
from app.features.meters.domain.model import SensorRecordsResponse, WaterQualityMeter
from app.share.response.model import ResponseApi


class WQMeterResponse(ResponseApi):
    meter: WaterQualityMeter


class WQMeterGetResponse(ResponseApi):
    meters: list[WaterQualityMeter]

class WQMeterRecordsResponse(ResponseApi):
    records: SensorRecordsResponse