from pydantic import BaseModel
from datetime import datetime
from app.share.response.model import ResponseApi

class Location(BaseModel):
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime_epoch: int
    localtime: str

class Condition(BaseModel):
    text: str
    icon: str
    code: int

class CurrentWeather(BaseModel):
    last_updated_epoch: int
    last_updated: str
    temp_c: float
    temp_f: float
    condition: Condition
    wind_kph: float
    wind_degree: int
    wind_dir: str
    humidity: int
    cloud: int

class DayForecast(BaseModel):
    maxtemp_c: float
    mintemp_c: float
    avgtemp_c: float
    maxwind_kph: float
    totalprecip_mm: float
    totalsnow_cm: float
    avgvis_km: float
    avghumidity: int
    daily_will_it_rain: int
    daily_chance_of_rain: int
    condition: Condition

class ForecastDay(BaseModel):
    date: str
    date_epoch: int
    day: DayForecast

class Forecast(BaseModel):
    forecastday: list[ForecastDay]

# Responses
class CurrentWeatherResponse(ResponseApi):
    data: dict = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "",
                "data": {
                    "location": {},
                    "current": {}
                }
            }
        }

class HistoricalWeatherResponse(ResponseApi):
    data: dict = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "",
                "data": {
                    "location": {},
                    "forecast": {}
                }
            }
        }