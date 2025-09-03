import math
import pandas as pd
from app.features.analysis.domain.enums import PeriodEnum
from app.features.analysis.domain.repository import AnalysisAverageRepository
from app.features.analysis.domain.model import (
    AveragePeriod,
    AverageRange,
    AverageResult,
    AvgPeriod,
    AvgPeriodAllResult,
    AvgPeriodResult,
    AvgResult,
    AvgSensor,
    Chart,
    Period,
    PredictionParam,
)
from app.share.meter_records.domain.enums import SensorType
from app.share.meter_records.domain.model import SensorIdentifier, SensorQueryParams
from app.share.meter_records.domain.repository import (
    MeterRecordsRepository,
)


class AnalysisAverage(AnalysisAverageRepository):
    def __init__(self, record_repo: MeterRecordsRepository):
        self.record_repo: MeterRecordsRepository = record_repo

    def _get_df(self, identifier: SensorIdentifier, params: SensorQueryParams):
        records = self.record_repo.query_records(identifier=identifier, params=params)

        rows = []
        sensor_type = params.sensor_type

        if sensor_type == SensorType.COLOR:
            raise ValueError("El análisis de color no está soportado")

        for ts, sensors in records.items():
            row = {"timestamp": int(ts)}
            if sensor_type is not None:
                sensor_record = getattr(sensors, sensor_type.value)
                row[sensor_type.value] = sensor_record.value if sensor_record else None

            else:
                for st in SensorType:
                    if st == SensorType.COLOR:
                        continue
                    sensor_record = getattr(sensors, st.value)
                    row[st.value] = sensor_record.value if sensor_record else None

            rows.append(row)

        return pd.DataFrame(rows)

    def _get_df_period(
        self,
        identifier: SensorIdentifier,
        params: SensorQueryParams,
        period_type: PeriodEnum = PeriodEnum.DAYS,
    ):
        df = self._get_df(
            identifier=identifier,
            params=params,
        )

        df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
        df = df.drop(columns=["timestamp"])
        df = df.set_index("datetime").sort_index()

        avg: pd.DataFrame

        if period_type == PeriodEnum.YEARS:
            avg = df.resample("Y").mean()
        elif period_type == PeriodEnum.MONTHS:
            avg = df.resample("ME").mean()
        else:
            avg = df.resample("D").mean()

        return avg

    def get_analysis(
        self, identifier: SensorIdentifier, average_range: AverageRange
    ) -> AverageResult:
        pass

    def create_average(
        self, identifier: SensorIdentifier, average_range: AverageRange
    ) -> AverageResult | list[AverageResult]:

        df = self._get_df(
            identifier=identifier,
            params=SensorQueryParams(
                start_date=average_range.start_date,
                end_date=average_range.end_date,
                sensor_type=average_range.sensor_type,
                ignore_limit=True,
            ),
        )

        sensor_type = average_range.sensor_type

        if sensor_type == SensorType.COLOR:
            raise ValueError("Sensor de color no esta implementado")

        if sensor_type is not None:

            average = df[sensor_type.value].mean()
            min = df[sensor_type.value].min()
            max = df[sensor_type.value].max()

            return AverageResult(
                sensor=sensor_type,
                period={
                    "start_date": average_range.start_date,
                    "end_date": average_range.end_date,
                },
                stats={"average": average, "min": min, "max": max},
                chart=[
                    Chart(
                        type="bar",
                        title=f"{sensor_type}: Average vs min/max",
                        labels=["Min", "Average", "Max"],
                        values=[min, average, max],
                    )
                ],
            )

        average_list = []

        for sensor_name in SensorType:
            if sensor_name == SensorType.COLOR:
                continue

            s_df = df[sensor_name]

            average = s_df.mean()
            min = s_df.min()
            max = s_df.max()

            average_list.append(
                AverageResult(
                    sensor=sensor_name,
                    period=Period(
                        start_date=average_range.start_date,
                        end_date=average_range.end_date,
                    ),
                    stats={"average": average, "min": min, "max": max},
                    charts=[
                        Chart(
                            type="bar",
                            title=f"{sensor_name}: Average vs min/max",
                            labels=["Min", "Average", "Max"],
                            values=[min, average, max],
                        )
                    ],
                )
            )

        return average_list

    def _safe_value(self, v):
        return None if (v is None or (isinstance(v, float) and math.isnan(v))) else v

    def create_average_period(
        self, identifier: SensorIdentifier, average_period: AveragePeriod
    ) -> AvgPeriodAllResult | AvgPeriodResult:

        df = self._get_df_period(
            identifier=identifier,
            params=SensorQueryParams(
                start_date=average_period.start_date,
                end_date=average_period.end_date,
                sensor_type=average_period.sensor_type,
                ignore_limit=True,
            ),
            period_type=average_period.period_type,
        )

        sensor_type = average_period.sensor_type

        if sensor_type == SensorType.COLOR:
            raise ValueError("Sensor de color no esta implementado")

        if sensor_type is not None:
            averages: list[AvgResult] = []

            labels_chart = []
            values_chart = []

            for index, row in df.iterrows():
                labels_chart.append(str(index))
                value = self._safe_value(row[sensor_type])
                values_chart.append(value)
                averages.append(AvgResult(date=index, value=value))

            return AvgPeriodResult(
                sensor=sensor_type,
                period=Period(
                    start_date=average_period.start_date,
                    end_date=average_period.end_date,
                ),
                period_type=average_period.period_type,
                averages=averages,
                charts=[
                    Chart(
                        type="line",
                        title=f"{sensor_type.value} average by {average_period.period_type.value}",
                        labels=labels_chart,
                        values=values_chart,
                    )
                ],
            )

        averages: list[AvgPeriod] = []

        labels_chart: list[float | None] = []
        values_chart_dic: dict[SensorType, list[float | None]] = {
            SensorType.CONDUCTIVITY: [],
            SensorType.PH: [],
            SensorType.TEMPERATURE: [],
            SensorType.TDS: [],
            SensorType.TURBIDITY: [],
        }

        for index, row in df.iterrows():
            labels_chart.append(str(index))

            conductivity = self._safe_value(row["conductivity"])
            ph = self._safe_value(row["ph"])
            temperature = self._safe_value(row["temperature"])
            tds = self._safe_value(row["tds"])
            turbidity = self._safe_value(row["turbidity"])

            values_chart_dic[SensorType.CONDUCTIVITY].append(conductivity)
            values_chart_dic[SensorType.PH].append(ph)
            values_chart_dic[SensorType.TEMPERATURE].append(temperature)
            values_chart_dic[SensorType.TDS].append(tds)
            values_chart_dic[SensorType.TURBIDITY].append(turbidity)

            averages.append(
                AvgPeriod(
                    date=index,
                    averages=AvgSensor(
                        conductivity=conductivity,
                        ph=ph,
                        temperature=temperature,
                        tds=tds,
                        turbidity=turbidity,
                    ),
                )
            )

        return AvgPeriodAllResult(
            period=Period(
                start_date=average_period.start_date,
                end_date=average_period.end_date,
            ),
            period_type=average_period.period_type,
            averages=averages,
            charts=[
                Chart(
                    type="line",
                    title=f"{sensor_name.value} average by {average_period.period_type.value}",
                    labels=labels_chart,
                    values=values_chart_dic[sensor_name],
                )
                for sensor_name in SensorType
                if sensor_name != SensorType.COLOR
            ],
        )

    def generate_prediction(
        self, identifier: SensorIdentifier, prediction_param: PredictionParam
    ):
        pass
