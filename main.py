from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, run_migrations
from app.models import base
from app.routes import health, weather
from app.services.scheduler_service import scheduler

base.Base.metadata.create_all(bind=engine)
run_migrations()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(weather.router, tags=["weather"])

@app.get("/")
def root():
    return {"message": "AI Weather Intelligence API"}


@app.on_event("startup")
def start_scheduler():
    print("🔥 Scheduler started")
    scheduler.start()