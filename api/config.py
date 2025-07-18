"""
Configuration management for GutIntel FastAPI application.
This module provides centralized configuration management with environment variable support
and proper validation for development vs production settings.
"""
import os
from typing import Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

class Settings(BaseModel):
    """Application settings with environment variable support."""
    
    # API Configuration
    api_title: str = "GutIntel API"
    api_description: str = "Gut Health Intelligence API - Comprehensive ingredient and microbiome data"
    api_version: str = "1.0.0"
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Server Configuration
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    debug: bool = Field(False, env="DEBUG")
    
    # CORS Configuration
    cors_origins: list = Field(["*"], env="CORS_ORIGINS")
    cors_methods: list = Field(["GET", "POST", "PUT", "DELETE"], env="CORS_METHODS")
    cors_headers: list = Field(["*"], env="CORS_HEADERS")
    
    # Request Configuration
    max_request_size: int = Field(10485760, env="MAX_REQUEST_SIZE")  # 10MB
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Cache Configuration
    cache_ttl: int = Field(300, env="CACHE_TTL")  # 5 minutes
    
    @validator('database_url')
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
            raise ValueError('Database URL must start with postgresql:// or postgresql+asyncpg://')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance AFTER environment is loaded
_settings = None

def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def is_development() -> bool:
    """Check if running in development mode."""
    return get_settings().debug

def is_production() -> bool:
    """Check if running in production mode."""
    return not get_settings().debug
