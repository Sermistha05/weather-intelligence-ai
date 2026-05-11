from apscheduler.schedulers.background import BackgroundScheduler
from app.services.weather_service import fetch_weather
from app.core.database import SessionLocal
from app.models.weather import Weather
import asyncio

cities = ["Delhi", "Mumbai", "Bangalore", "Jaipur", "Chandigarh"]

def collect_weather():
    print("🚀 Scheduler triggered")
    db = SessionLocal()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for city in cities:
            weather = loop.run_until_complete(fetch_weather(city))
            record = Weather(**weather)
            db.add(record)

        db.commit()
        print("✅ Weather data collected automatically")

    finally:
        db.close() 
scheduler = BackgroundScheduler()
scheduler.add_job(collect_weather, "interval", minutes=10)