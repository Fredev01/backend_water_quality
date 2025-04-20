import httpx
import os
from datetime import datetime, timedelta
from app.share.weatherapi.domain.model import CurrentWeatherResponse, HistoricalWeatherResponse
from app.share.weatherapi.domain.repository import WeatherRepo

class WeatherService(WeatherRepo):
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.weatherapi.com/v1"

    async def get_current_weather(self, lat: float, lon: float) -> CurrentWeatherResponse:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/current.json",
                    params={
                        "key": self.api_key,
                        "q": f"{lat},{lon}"
                    }
                )                
                response.raise_for_status()
                data = response.json()

                return CurrentWeatherResponse(
                    success=True,
                    message="",
                    data=data   
                )                

        except Exception as e:
            return CurrentWeatherResponse(
                success=False,
                message=f"Error inesperado: {str(e)}",
                data={}
            )
        
    async def get_historical_weather(self, lat: float, lon: float, last_days: int) -> HistoricalWeatherResponse:
        try:
            if last_days < 1 or last_days > 3:
                raise ValueError("Solo se permiten entre 1 y 3 días históricos")

            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=last_days - 1)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/history.json",
                    params={
                        "key": self.api_key,
                        "q": f"{lat},{lon}",
                        "dt": start_date.isoformat(),
                        "end_dt": end_date.isoformat()
                    }
                )
                response.raise_for_status()
                data = response.json()
                return HistoricalWeatherResponse(
                    success=True,
                    message="",
                    data=data
                )
        except Exception as e:
            return HistoricalWeatherResponse(
                success=False,
                message=str(e),
                data=None
            )