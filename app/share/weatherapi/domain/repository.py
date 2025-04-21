from abc import ABC, abstractmethod
from app.share.weatherapi.domain.model import CurrentWeatherResponse, HistoricalWeatherResponse

class WeatherRepo(ABC):
    @abstractmethod
    def get_current_weather(self, lat: float, lon: float) -> CurrentWeatherResponse:
        pass

    @abstractmethod
    def get_historical_weather(self, lat: float, lon: float, last_days: int) -> HistoricalWeatherResponse:
        pass
