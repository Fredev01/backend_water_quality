from app.features.analysis.domain.model import AverageRange
from app.share.meter_records.domain.enums import SensorType
from app.share.meter_records.domain.repository import (
    RecordDataframeRepository,
)
from app.features.analysis.domain.repository import AnalysisAvarageRepository
from app.share.meter_records.domain.model import (
    AverageResult,
    Chart,
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
                    period={
                        "start_date": avarage_range.start_date,
                        "end_date": avarage_range.end_date,
                    },
                    stats={"average": average, "min": min, "max": max},
                    chart=[
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
