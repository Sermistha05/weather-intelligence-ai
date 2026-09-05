import joblib
import numpy as np
import pandas as pd
import sqlite3
import os
from datetime import datetime, timezone

temp_model = joblib.load("temperature_model.pkl")

_rain_model = None

FEATURES = [
    "humidity", "pressure", "wind_speed", "rain_probability", "uv_index",
    "hour", "day", "month",
    "hour_sin", "hour_cos", "month_sin", "month_cos",
    "temp_lag_1", "temp_lag_3", "temp_lag_6", "temp_lag_24",
    "temp_roll_6", "temp_roll_24",
]

def _get_rain_model():
    global _rain_model
    if _rain_model is None:
        if not os.path.exists("rain_model.pkl"):
            raise FileNotFoundError("rain_model.pkl not found. Run app/ml/train_rain_model.py first.")
        _rain_model = joblib.load("rain_model.pkl")
    return _rain_model

def _build_rain_features(humidity, pressure, wind_speed, hour):
    return pd.DataFrame({"hour": [hour], "humidity": [humidity], "pressure": [pressure], "wind_speed": [wind_speed]})

def predict_temperature(humidity, pressure, wind_speed, hour):
    # Legacy endpoint: fill missing features with 0 (kept for /predict/temperature)
    now = datetime.now(timezone.utc)
    row = {
        "humidity": humidity, "pressure": pressure, "wind_speed": wind_speed,
        "rain_probability": 0.0, "uv_index": 0.0,
        "hour": hour, "day": now.day, "month": now.month,
        "hour_sin": np.sin(2 * np.pi * hour / 24),
        "hour_cos": np.cos(2 * np.pi * hour / 24),
        "month_sin": np.sin(2 * np.pi * now.month / 12),
        "month_cos": np.cos(2 * np.pi * now.month / 12),
        "temp_lag_1": 0.0, "temp_lag_3": 0.0, "temp_lag_6": 0.0, "temp_lag_24": 0.0,
        "temp_roll_6": 0.0, "temp_roll_24": 0.0,
    }
    prediction = temp_model.predict(pd.DataFrame([row])[FEATURES])
    return round(float(prediction[0]), 1)

def predict_rain(humidity, pressure, wind_speed, hour) -> int:
    model = _get_rain_model()
    prediction = model.predict(_build_rain_features(humidity, pressure, wind_speed, hour))
    return int(prediction[0])

async def predict_temperature_by_city(city: str, fetch_weather_fn) -> dict:
    weather = await fetch_weather_fn(city)
    now = datetime.now(timezone.utc)
    hour = now.hour

    # Fetch last 24 temperature readings for this city from DB
    conn = sqlite3.connect("weather.db")
    hist = pd.read_sql_query(
        "SELECT temperature FROM weather WHERE location = ? AND temperature IS NOT NULL ORDER BY timestamp DESC LIMIT 24",
        conn, params=(city,)
    )
    conn.close()

    temps = hist["temperature"].tolist()  # index 0 = most recent

    def _lag(n):
        return float(temps[n - 1]) if len(temps) >= n else (float(temps[-1]) if temps else 0.0)

    def _roll(n):
        vals = temps[:n]
        return float(np.mean(vals)) if vals else 0.0

    row = {
        "humidity": weather["humidity"],
        "pressure": weather["pressure"],
        "wind_speed": weather["wind_speed"],
        "rain_probability": weather.get("rain_probability", 0.0),
        "uv_index": weather.get("uv_index", 0.0),
        "hour": hour,
        "day": now.day,
        "month": now.month,
        "hour_sin": np.sin(2 * np.pi * hour / 24),
        "hour_cos": np.cos(2 * np.pi * hour / 24),
        "month_sin": np.sin(2 * np.pi * now.month / 12),
        "month_cos": np.cos(2 * np.pi * now.month / 12),
        "temp_lag_1": _lag(1),
        "temp_lag_3": _lag(3),
        "temp_lag_6": _lag(6),
        "temp_lag_24": _lag(24),
        "temp_roll_6": _roll(6),
        "temp_roll_24": _roll(24),
    }

    prediction = temp_model.predict(pd.DataFrame([row])[FEATURES])
    return {
        "city": city,
        "current_weather": weather,
        "predicted_temperature": round(float(prediction[0]), 1),
    }