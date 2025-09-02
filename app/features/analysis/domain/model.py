from typing import ClassVar

from app.share.meter_records.domain.enums import PeriodEnum
from app.share.meter_records.domain.model import SensorQueryParams, SensorIdentifier


class AverageRange(SensorQueryParams):
    limit: ClassVar[int] = None
    index: ClassVar[str] = None
    ignore_limit: ClassVar[bool] = None


class AveragePeriod(AverageRange):
    period_type: PeriodEnum = PeriodEnum.DAYS


class AverageIdentifier(SensorIdentifier):
    sensor_name: ClassVar[str] = None
    user_id: ClassVar[str] = None
