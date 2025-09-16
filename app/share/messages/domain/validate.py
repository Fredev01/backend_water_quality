from app.share.socketio.domain.model import RecordBody
from app.share.messages.domain.model import AlertType, PriorityParameters, RangeValue
from app.share.meter_records.domain.enums import SensorType


class RecordValidation:

    @classmethod
    def _get_alert_level_for_value(
        cls,
        ranges: dict[AlertType, dict[ParameterType, RangeValue]],
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
    def validate(cls, record: RecordBody, levels_to_check: list[AlertType], parameters_and_ranges: dict[AlertType, dict[ParameterType, RangeValue]]) -> AlertType | None:
        values: dict[ParameterType, float] = {
            ParameterType.TEMPERATURE: record.temperature,
            ParameterType.TDS: record.tds,
            ParameterType.CONDUCTIVITY: record.conductivity,
            ParameterType.PH: record.ph,
            ParameterType.TURBIDITY: record.turbidity,
        }

        counts: dict[AlertType, int] = {level: 0 for level in levels_to_check}
        count_priority_params = 0

        for param, value in values.items():
            level = cls._get_alert_level_for_value(
                parameters_and_ranges, param, value, levels_to_check)

            if level is None:
                continue
            if param in PriorityParameters.parameters and (level == AlertType.DANGEROUS or level == AlertType.POOR):
                count_priority_params += 1

            counts[level] += 1

        level, count = max(counts.items(), key=lambda item: item[1])
        if count_priority_params > 0:
            print(
                f"priority params count: {count_priority_params} level: {level}")
            return level

        return level if count >= 3 else None
