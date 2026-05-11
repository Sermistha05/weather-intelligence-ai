from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.database import Base

class Weather(Base):
    __tablename__ = "weather"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    wind_speed = Column(Float)
    rain_probability = Column(Float)
    uv_index = Column(Float)
    rain = Column(Integer, default=0)  # 0 = no rain, 1 = rain
    timestamp = Column(DateTime, default=datetime.utcnow)
