from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine
from app.models import base
from app.routes import health, weather

base.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.include_router(health.router, tags=["health"])
app.include_router(weather.router, tags=["weather"])

@app.get("/")
def root():
    return {"message": "AI Weather Intelligence API"}