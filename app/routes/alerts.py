from fastapi import APIRouter, HTTPException
from app.services.weather_service import fetch_weather
from app.services.prediction_service import predict_temperature_by_city, predict_rain_proba
from app.services.alert_service import evaluate_alerts
from datetime import datetime, timezone

router = APIRouter()


@router.get("/alerts")
async def get_alerts(city: str):
    if not city.strip():
        raise HTTPException(status_code=400, detail="City name is required.")

    try:
        weather = await fetch_weather(city)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch weather for '{city}': {e}")

    try:
        async def _cached_weather(_city):
            return weather

        temp_result = await predict_temperature_by_city(city, _cached_weather)
        predicted_temp = temp_result["predicted_temperature"]
    except Exception:
        predicted_temp = weather["temperature"]

    try:
        hour = datetime.now(timezone.utc).hour
        rain_result = predict_rain_proba(
            humidity=weather["humidity"],
            pressure=weather["pressure"],
            wind_speed=weather["wind_speed"],
            hour=hour,
        )
        rain_probability_pct = rain_result["rain_probability_pct"]
    except Exception:
        rain_probability_pct = 0.0

    alerts = evaluate_alerts(
        wind_speed=weather["wind_speed"],
        humidity=weather["humidity"],
        temp=weather["temperature"],
        predicted_temp=predicted_temp,
        rain_probability_pct=rain_probability_pct,
    )

    return {"city": city, "alerts": alerts}
