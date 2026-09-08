from pydantic_settings import BaseSettings 
# This file defines the configuration settings for the application using Pydantic's BaseSettings.
# Pydantics BaseSettings allows us to define settings that can be loaded from environment variables or a 
# .env file, making it easy to manage configuration in different environments (development, staging, production).

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Weather Intelligence"
    VERSION: str = "1.0.0"
    DATABASE_URL: str
    OPENWEATHER_API_KEY: str
    GEMINI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
