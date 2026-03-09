from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
# sqlalchemy is used for database interactions. We define the database engine, session, and base class for our models here. 
# The get_db function provides a way to get a database session that can be used in our API routes, ensuring that the session
# is properly closed after use.
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
