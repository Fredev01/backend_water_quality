from pydantic import BaseModel
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


class Current(BaseModel):
    last_updated_epoch: int
    last_updated: str
    temp_c: float
    temp_f: float
    is_day: int | None = None
    condition: Condition
    wind_mph: float | None = None
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float | None = None
    pressure_in: float | None = None
    precip_mm: float | None = None
    precip_in: float | None = None
    humidity: int
    cloud: int
    feelslike_c: float | None = None
    feelslike_f: float | None = None
    windchill_c: float | None = None
    windchill_f: float | None = None
    heatindex_c: float | None = None
    heatindex_f: float | None = None
    dewpoint_c: float | None = None
    dewpoint_f: float | None = None
    vis_km: float | None = None
    vis_miles: float | None = None
    uv: float | None = None
    gust_mph: float | None = None
    gust_kph: float | None = None


class CurrentWeather(BaseModel):
    location: Location
    current: Current


class DayForecast(BaseModel):
    maxtemp_c: float
    maxtemp_f: float | None = None
    mintemp_c: float
    mintemp_f: float | None = None
    avgtemp_c: float
    avgtemp_f: float | None = None
    maxwind_mph: float | None = None
    maxwind_kph: float
    totalprecip_mm: float
    totalprecip_in: float | None = None
    totalsnow_cm: float
    avgvis_km: float
    avgvis_miles: float | None = None
    avghumidity: int
    daily_will_it_rain: int
    daily_chance_of_rain: int
    daily_will_it_snow: int | None = None
    daily_chance_of_snow: int | None = None
    condition: Condition
    uv: float | None = None


class Astro(BaseModel):
    sunrise: str
    sunset: str
    moonrise: str
    moonset: str
    moon_phase: str
    moon_illumination: int | None = None


class HourForecast(BaseModel):
    time_epoch: int
    time: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: Condition
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    precip_mm: float
    precip_in: float
    snow_cm: float | None = None
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    windchill_c: float
    windchill_f: float
    heatindex_c: float
    heatindex_f: float
    dewpoint_c: float
    dewpoint_f: float
    will_it_rain: int
    chance_of_rain: int
    will_it_snow: int
    chance_of_snow: int
    vis_km: float
    vis_miles: float
    gust_mph: float
    gust_kph: float
    uv: float


class ForecastDay(BaseModel):
    date: str
    date_epoch: int
    day: DayForecast
    astro: Astro
    hour: list[HourForecast]


class Forecast(BaseModel):
    forecastday: list[ForecastDay]


class HistoricalWeather(BaseModel):
    location: Location | None = None
    forecast: Forecast | None = None
    current: Current | None = None


# Responses


class CurrentWeatherResponse(ResponseApi):
    success: bool
    message: str
    data: CurrentWeather | None


class HistoricalWeatherResponse(ResponseApi):
    success: bool
    message: str
    data: HistoricalWeather | None
