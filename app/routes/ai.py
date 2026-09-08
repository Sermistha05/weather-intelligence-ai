from fastapi import APIRouter, HTTPException
from app.services.weather_service import fetch_weather
from app.services.prediction_service import predict_temperature_by_city, predict_rain_proba
from app.services.ai_service import generate_insight
from datetime import datetime, timezone

router = APIRouter()


@router.get("/ai/insight")
async def get_ai_insight(city: str):
    if not city.strip():
        raise HTTPException(status_code=400, detail="City name is required.")

    try:
        # Fetch current weather once — reused for both ML calls below
        weather = await fetch_weather(city)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch weather for '{city}': {e}")

    # Temperature ML prediction — pass the already-fetched weather to avoid a
    # second OWM call that could return a different snapshot and corrupt the prediction
    try:
        async def _cached_weather(_city):
            return weather

        temp_result = await predict_temperature_by_city(city, _cached_weather)
        predicted_temp = temp_result["predicted_temperature"]
    except Exception:
        predicted_temp = weather["temperature"]  # graceful fallback: use current temp

    # Rain ML prediction — uses already-fetched weather values directly
    try:
        hour = datetime.now(timezone.utc).hour
        rain_result = predict_rain_proba(
            humidity=weather["humidity"],
            pressure=weather["pressure"],
            wind_speed=weather["wind_speed"],
            hour=hour,
        )
        will_rain = rain_result["will_rain"]
        rain_probability_pct = rain_result["rain_probability_pct"]
    except Exception:
        will_rain = bool(weather.get("rain", 0))
        rain_probability_pct = 0.0

    insight = generate_insight(
        city=city,
        temp=weather["temperature"],
        humidity=weather["humidity"],
        pressure=weather["pressure"],
        wind_speed=weather["wind_speed"],
        rain=weather.get("rain", 0),
        predicted_temp=predicted_temp,
        rain_probability_pct=rain_probability_pct,
        will_rain=will_rain,
    )

    return {"city": city, "insight": insight}
