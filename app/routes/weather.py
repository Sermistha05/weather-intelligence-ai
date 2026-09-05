from app.services.prediction_service import predict_temperature, predict_rain, predict_rain_proba, predict_temperature_by_city
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.weather import Weather
from app.schemas.weather import WeatherResponse
from app.services.weather_service import fetch_weather
from datetime import datetime, timezone

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
    return {"predicted_temperature": predicted_temp}

@router.get("/predict/rain")
def get_rain_prediction(
    humidity: float,
    pressure: float,
    wind_speed: float,
    hour: int
):
    try:
        result = predict_rain(humidity, pressure, wind_speed, hour)
        return {"will_rain": bool(result)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/predict/temperature/by-city")
async def get_temperature_prediction_by_city(city: str):
    try:
        return await predict_temperature_by_city(city, fetch_weather)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/predict/rain/by-city")
async def get_rain_prediction_by_city(city: str):
    try:
        weather = await fetch_weather(city)
        hour = datetime.now(timezone.utc).hour
        result = predict_rain_proba(
            humidity=weather["humidity"],
            pressure=weather["pressure"],
            wind_speed=weather["wind_speed"],
            hour=hour
        )
        return {"city": city, "will_rain": result["will_rain"], "rain_probability_pct": result["rain_probability_pct"]}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))