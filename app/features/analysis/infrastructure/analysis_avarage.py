from app.features.analysis.domain.model import AvarageRange
from app.share.meter_records.domain.repository import MeterRecordsRepository
from app.features.analysis.domain.repository import AnalysisAvarageRepository
from app.share.meter_records.domain.model import (
    AvarageResult,
    SensorIdentifier,
    SensorQueryParams,
)


class AnalysisAvarage(AnalysisAvarageRepository):
    def __init__(self, record_repo: MeterRecordsRepository):
        self.record_repo: MeterRecordsRepository = record_repo

    def get_analysis(
        self, identifier: SensorIdentifier, query_params: AvarageRange
    ) -> AvarageResult:
        pass

    def create_avarage(
        self, identifier: SensorIdentifier, avarage_range: AvarageRange
    ) -> AvarageResult:

        records = self.record_repo.query_sensor_records(
            identifier=identifier,
            query_params=SensorQueryParams(
                start_date=avarage_range.start_date,
                end_date=avarage_range.end_date,
                sensor_type=avarage_range.sensor_type,
                ignore_limit=True,
            ),
        )

        print(records)

        return AvarageResult(
            sensor="temperature",
            period={
                "start_date": avarage_range.start_date,
                "end_date": avarage_range.end_date,
            },
            stats={
                "average": 25.5,
                "min": 20.0,
                "max": 30.0,
                "out_of_range_percent": 5.0,
            },
            chart={
                "type": "line",
                "labels": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "values": [22.5, 24.0, 26.5],
            },
        )
