from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_migrations():
    """Add new columns to existing SQLite DB without dropping data."""
    with engine.connect() as conn:
        columns = [row[1] for row in conn.execute(text("PRAGMA table_info(weather)"))]
        if "rain" not in columns:
            conn.execute(text("ALTER TABLE weather ADD COLUMN rain INTEGER DEFAULT 0"))
            conn.commit()
