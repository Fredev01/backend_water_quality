from enum import Enum


class PeriodEnum(str, Enum):
    DAYS = "days"
    MONTHS = "months"
    YEARS = "years"


class CorrMethodEnum(str, Enum):
    SPEARMAN = "spearman"
    PEARSON = "pearson"


class AnalysisEnum(str, Enum):
    AVERAGE = "average"
    AVERAGE_PERIOD = "average_period"
    PREDICTION = "prediction"
    CORRELATION = "correlation"
