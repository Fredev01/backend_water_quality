import math
from app.features.analysis.domain.model import AveragePeriod, AverageRange
from app.share.meter_records.domain.enums import SensorType
from app.share.meter_records.domain.repository import (
    RecordDataframeRepository,
)
from app.features.analysis.domain.repository import AnalysisAvarageRepository
from app.share.meter_records.domain.model import (
    AverageResult,
    AvgPeriod,
    AvgPeriodAllResult,
    AvgPeriodResult,
    AvgResult,
    AvgSensor,
    Chart,
    Period,
    SensorIdentifier,
    SensorQueryParams,
)


class AnalysisAvarage(AnalysisAvarageRepository):
    def __init__(self, record_dataframe: RecordDataframeRepository):
        self.record_dataframe: RecordDataframeRepository = record_dataframe

    def get_analysis(
        self, identifier: SensorIdentifier, query_params: AverageRange
    ) -> AverageResult:
        pass

    def create_avarage(
        self, identifier: SensorIdentifier, avarage_range: AverageRange
    ) -> AverageResult | list[AverageResult]:

        df = self.record_dataframe.get_df(
            identifier=identifier,
            params=SensorQueryParams(
                start_date=avarage_range.start_date,
                end_date=avarage_range.end_date,
                sensor_type=avarage_range.sensor_type,
                ignore_limit=True,
            ),
        )

        print(df)

        sensor_type = avarage_range.sensor_type

        if sensor_type == SensorType.COLOR:
            raise ValueError("Sensor de color no esta implementado")

        if sensor_type is not None:

            average = df[sensor_type.value].mean()
            min = df[sensor_type.value].min()
            max = df[sensor_type.value].max()

            return AverageResult(
                sensor=sensor_type,
                period={
                    "start_date": avarage_range.start_date,
                    "end_date": avarage_range.end_date,
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
                        start_date=avarage_range.start_date,
                        end_date=avarage_range.end_date,
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

    def creata_avarage_period(
        self, identifier: SensorIdentifier, avarage_period: AveragePeriod
    ) -> AvgPeriodAllResult | AvgPeriodResult:

        df = self.record_dataframe.get_df_period(
            identifier=identifier,
            params=SensorQueryParams(
                start_date=avarage_period.start_date,
                end_date=avarage_period.end_date,
                sensor_type=avarage_period.sensor_type,
                ignore_limit=True,
            ),
            period_type=avarage_period.period_type,
        )

        sensor_type = avarage_period.sensor_type

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
                    start_date=avarage_period.start_date,
                    end_date=avarage_period.end_date,
                ),
                period_type=avarage_period.period_type,
                averages=averages,
                charts=[
                    Chart(
                        type="line",
                        title=f"{sensor_type.value} avarage by {avarage_period.period_type.value}",
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
                start_date=avarage_period.start_date,
                end_date=avarage_period.end_date,
            ),
            period_type=avarage_period.period_type,
            averages=averages,
            charts=[
                Chart(
                    type="line",
                    title=f"{sensor_name.value} avarage by {avarage_period.period_type.value}",
                    labels=labels_chart,
                    values=values_chart_dic[sensor_name],
                )
                for sensor_name in SensorType
                if sensor_name != SensorType.COLOR
            ],
        )
