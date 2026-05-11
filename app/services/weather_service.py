import httpx
from app.core.config import settings

async def fetch_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    
    return {
        "location": city,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "rain_probability": data.get("rain", {}).get("1h", 0.0),
        "uv_index": 0.0,
        "rain": 1 if "rain" in data else 0
    }
