from pydantic import BaseModel


class SensorQueryParams(BaseModel):
    limit: int = 10
    index: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    sensor_type: str | None = None


class SensorIdentifier(BaseModel):
    workspace_id: str
    meter_id: str
    user_id: str
    sensor_name: str | None = None
