from fastapi import APIRouter, HTTPException
from app.services.weather_service import fetch_forecast

router = APIRouter()


@router.get("/forecast")
async def get_forecast(city: str):
    if not city.strip():
        raise HTTPException(status_code=400, detail="City name is required.")
    try:
        slots = await fetch_forecast(city)
        return {"city": city, "forecast": slots}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
