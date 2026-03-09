from app.services.prediction_service import predict_temperature
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.weather import Weather
from app.schemas.weather import WeatherResponse
from app.services.weather_service import fetch_weather

router = APIRouter()

@router.get("/weather/current", response_model=WeatherResponse)
async def get_current_weather(city: str, db: Session = Depends(get_db)):
    try:
        weather_data = await fetch_weather(city)
        
        db_weather = Weather(**weather_data)
        db.add(db_weather)
        db.commit()
        db.refresh(db_weather)
        
        return db_weather
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/weather/history", response_model=list[WeatherResponse])
def get_weather_history(db: Session = Depends(get_db)):
    try:
        weather_records = db.query(Weather).all()
        return weather_records
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/predict/temperature")
def get_temperature_prediction(
    humidity: float,
    pressure: float,
    wind_speed: float,
    hour: int
):
    predicted_temp = predict_temperature(humidity, pressure, wind_speed, hour)

    return {
        "predicted_temperature": predicted_temp
    }