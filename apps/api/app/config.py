import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # API
    API_VERSION: str = "0.1.0"
    API_TITLE: str = "Pet Lost System API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str

    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # CORS
    CORS_ORIGINS: list[str]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Features
    ALERT_RADIUS_DEFAULT_KM: float = 5.0
    ALERT_PROCESSING_TIMEOUT_SECONDS: int = 5
    IMAGE_SEARCH_TIMEOUT_SECONDS: int = 3


    # Notifications
    SEND_SMS: bool = False
    SEND_EMAILS: bool = False
    SEND_PUSH_NOTIFICATIONS: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
