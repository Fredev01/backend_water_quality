import pandas as pd
from app.share.meter_records.domain.enums import SensorType
from app.share.meter_records.domain.model import SensorIdentifier, SensorQueryParams
from app.share.meter_records.domain.repository import (
    MeterRecordsRepository,
    RecordDataframeRepository,
)


class RecordDataframe(RecordDataframeRepository):
    def __init__(self, record_repo: MeterRecordsRepository):
        self.record_repo: MeterRecordsRepository = record_repo

    def get_df(self, identifier: SensorIdentifier, params: SensorQueryParams):
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
