from pydantic import BaseModel
from datetime import datetime

class WeatherCreate(BaseModel):
    location: str
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    rain_probability: float
    uv_index: float

class WeatherResponse(BaseModel):
    id: int
    location: str
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    rain_probability: float
    uv_index: float
    timestamp: datetime
    
    class Config:
        from_attributes = True
