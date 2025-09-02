from enum import Enum


class SensorType(str, Enum):
    COLOR = "color"
    CONDUCTIVITY = "conductivity"
    PH = "ph"
    TEMPERATURE = "temperature"
    TDS = "tds"
    TURBIDITY = "turbidity"


class PeriodEnum(str, Enum):
    DAYS = "days"
    MONTHS = "months"
    YEARS = "years"
