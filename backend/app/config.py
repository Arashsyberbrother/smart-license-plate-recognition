"""
Application configuration
تنظیمات برنامه
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file"""

    # Application
    APP_NAME: str = "Iranian License Plate Recognition System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./data/license_plates.db"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT: int = 5

    # File upload
    UPLOAD_DIR: str = "uploads/"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

    # ML Model
    MODEL_PATH: str = "models/"
    CONFIDENCE_THRESHOLD: float = 0.85
    IOU_THRESHOLD: float = 0.45

    # Cache
    CACHE_TTL: int = 300  # seconds
    CACHE_MAX_SIZE: int = 1000

    # Security
    API_KEY: str = ""

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
