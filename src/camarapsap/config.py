"""Configuration settings for CamaraPSAP API."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API version identifiers
    device_version_id: str = "vwip"
    location_version_id: str = "vwip"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings
    database_url: str = "postgresql://camarapsap:camarapsap@localhost:5432/camarapsap"
    
    # Redis settings
    redis_url: str = "redis://localhost:6380/0"
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
