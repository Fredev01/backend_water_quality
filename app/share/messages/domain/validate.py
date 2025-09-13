from app.share.socketio.domain.model import RecordBody
from app.share.messages.domain.model import AlertType, RangeValue, Ranges


class RecordValidation:
    @classmethod
    def _define_ranges(cls) -> dict[AlertType, dict[str, tuple[float, float]]]:
        return {
            AlertType.DANGEROUS: {
                "temperature": (0, 5),
                "tds": (0, 50),
                "conductivity": (0, 50),
                "ph": (0, 4.5),
                "turbidity": (0, 1),
            },
            AlertType.POOR: {
                "temperature": (5, 15),
                "tds": (50, 150),
                "conductivity": (50, 500),
                "ph": (4.5, 6.5),
                "turbidity": (1, 5),
            },
            AlertType.MODERATE: {
                "temperature": (15, 25),
                "tds": (150, 300),
                "conductivity": (500, 1500),
                "ph": (6.5, 8.5),
                "turbidity": (5, 10),
            },
            AlertType.GOOD: {
                "temperature": (25, 35),
                "tds": (300, 500),
                "conductivity": (1500, 3000),
                "ph": (8.5, 10),
                "turbidity": (10, 50),
            },
            AlertType.EXCELLENT: {
                "temperature": (35, float("inf")),
                "tds": (500, float("inf")),
                "conductivity": (3000, float("inf")),
                "ph": (10, float("inf")),
                "turbidity": (50, float("inf")),
            },
        }

    @classmethod
    def _get_alert_level_for_value(
        cls,
        ranges: dict[AlertType, dict[str, RangeValue]],
        param: str,
        value: float,
        levels_to_check: list[AlertType],
    ) -> AlertType | None:

        result = None

        for level in levels_to_check:
            range_value = ranges[level][param]
            if range_value.min <= value < range_value.max:
                result = level
                break

        return result

    @classmethod
    def validate(cls, record: RecordBody, levels_to_check: list[AlertType], parameters_and_ranges: dict[str, dict[str, RangeValue]]) -> AlertType | None:
        values: dict[str, float] = {
            "temperature": record.temperature,
            "tds": record.tds,
            "conductivity": record.conductivity,
            "ph": record.ph,
            "turbidity": record.turbidity,
        }

        counts: dict[AlertType, int] = {level: 0 for level in levels_to_check}

        for param, value in values.items():
            level = cls._get_alert_level_for_value(
                parameters_and_ranges, param, value, levels_to_check)

            if level is None:
                continue

            counts[level] += 1

        level, count = max(counts.items(), key=lambda item: item[1])

        return level if count >= 3 else None
