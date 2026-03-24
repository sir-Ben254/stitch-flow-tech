"""
Core configuration for StitchFlow Backend
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "StitchFlow"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Database
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Daraja API (Safaricom)
    DARAJA_CONSUMER_KEY: str = os.getenv("DARAJA_CONSUMER_KEY", "")
    DARAJA_CONSUMER_SECRET: str = os.getenv("DARAJA_CONSUMER_SECRET", "")
    DARAJA_SHORTCODE: str = os.getenv("DARAJA_SHORTCODE", "")
    DARAJA_CALLBACK_URL: str = os.getenv("DARAJA_CALLBACK_URL", "")
    DARAJA_PASSKEY: str = os.getenv("DARAJA_PASSKEY", "")
    DARAJA_ENVIRONMENT: str = os.getenv("DARAJA_ENVIRONMENT", "sandbox")
    
    # File Storage
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
    ALLOWED_MIME_TYPES: list = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/bmp"]
    UPLOAD_BUCKET: str = os.getenv("UPLOAD_BUCKET", "uploads")
    OUTPUT_BUCKET: str = os.getenv("OUTPUT_BUCKET", "outputs")
    
    # Rate Limiting
    RATE_LIMIT_UPLOAD: int = 5  # per minute
    RATE_LIMIT_API: int = 60    # per minute
    
    # System Mode
    SYSTEM_MODE: str = os.getenv("SYSTEM_MODE", "LOW")  # LOW or HIGH
    
    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()


settings = get_settings()
