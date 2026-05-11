import joblib
import pandas as pd
import os

temp_model = joblib.load("temperature_model.pkl")

_rain_model = None

def _get_rain_model():
    global _rain_model
    if _rain_model is None:
        if not os.path.exists("rain_model.pkl"):
            raise FileNotFoundError("rain_model.pkl not found. Run app/ml/train_rain_model.py first.")
        _rain_model = joblib.load("rain_model.pkl")
    return _rain_model

def _build_features(humidity, pressure, wind_speed, hour):
    return pd.DataFrame({"hour": [hour], "humidity": [humidity], "pressure": [pressure], "wind_speed": [wind_speed]})

def predict_temperature(humidity, pressure, wind_speed, hour):
    prediction = temp_model.predict(_build_features(humidity, pressure, wind_speed, hour))
    return round(float(prediction[0]), 1)

def predict_rain(humidity, pressure, wind_speed, hour) -> int:
    model = _get_rain_model()
    prediction = model.predict(_build_features(humidity, pressure, wind_speed, hour))
    return int(prediction[0])

async def predict_temperature_by_city(city: str, fetch_weather_fn) -> dict:
    from datetime import datetime, timezone
    weather = await fetch_weather_fn(city)
    hour = datetime.now(timezone.utc).hour
    predicted_temp = predict_temperature(weather["humidity"], weather["pressure"], weather["wind_speed"], hour)
    return {
        "city": city,
        "current_weather": weather,
        "predicted_temperature": predicted_temp
    }