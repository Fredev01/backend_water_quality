
from app.features.meters.domain.model import WaterQualityMeter
from app.share.response.model import ResponseApi


class WQMeterCreateResponse(ResponseApi):
    meter: WaterQualityMeter


class WQMeterGetResponse(ResponseApi):
    meters: list[WaterQualityMeter]
