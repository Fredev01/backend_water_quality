from enum import Enum


class PeriodEnum(str, Enum):
    DAYS = "days"
    MONTHS = "months"
    YEARS = "years"
