import requests
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.weather import Weather

# Cities with latitude and longitude
CITIES = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "London": {"lat": 51.5072, "lon": -0.1276},
    "New York": {"lat": 40.7128, "lon": -74.0060},
}

# Date range: Last 2 years
END_DATE = datetime.now().date()
START_DATE = END_DATE - timedelta(days=730)


def fetch_city_weather(city_name, lat, lon):
    print(f"\n🌍 Fetching historical data for {city_name}...")

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "surface_pressure",
            "wind_speed_10m",
            "precipitation"
        ],
        "timezone": "auto"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"❌ Failed for {city_name}")
        return pd.DataFrame()

    data = response.json()

    hourly = data.get("hourly", {})

    df = pd.DataFrame({
        "timestamp": hourly.get("time", []),
        "temperature": hourly.get("temperature_2m", []),
        "humidity": hourly.get("relative_humidity_2m", []),
        "pressure": hourly.get("surface_pressure", []),
        "wind_speed": hourly.get("wind_speed_10m", []),
        "precipitation": hourly.get("precipitation", [])
    })

    df["location"] = city_name

    return df


def insert_into_database(df, db: Session):
    inserted = 0

    for _, row in df.iterrows():

        # Skip rows with missing values
        if pd.isna(row["temperature"]):
            continue

        timestamp = datetime.fromisoformat(row["timestamp"])

        # Prevent duplicate rows
        existing = db.query(Weather).filter(
            Weather.location == row["location"],
            Weather.timestamp == timestamp
        ).first()

        if existing:
            continue

        weather = Weather(
            location=row["location"],
            temperature=float(row["temperature"]),
            humidity=float(row["humidity"]),
            pressure=float(row["pressure"]),
            wind_speed=float(row["wind_speed"]),
            rain_probability=float(row["precipitation"]),
            uv_index=0.0,
            rain=1 if row["precipitation"] > 0 else 0,
            timestamp=timestamp
        )

        db.add(weather)
        inserted += 1

    db.commit()

    return inserted


def main():
    db = SessionLocal()

    total_inserted = 0

    try:
        for city, coords in CITIES.items():

            df = fetch_city_weather(
                city,
                coords["lat"],
                coords["lon"]
            )

            if df.empty:
                continue

            inserted = insert_into_database(df, db)

            total_inserted += inserted

            print(f"✅ Inserted {inserted} rows for {city}")

        print(f"\n🎉 Total rows inserted: {total_inserted}")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    main()