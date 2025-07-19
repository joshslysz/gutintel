"""
Configuration management for GutIntel FastAPI application.
This module provides centralized configuration management with environment variable support
and proper validation for development vs production settings.
"""
import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables FIRST
# Look for .env file in parent directory (project root)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    api_title: str = "GutIntel API"
    api_description: str = "Gut Health Intelligence API - Comprehensive ingredient and microbiome data"
    api_version: str = "1.0.0"
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://postgres.nnzjneddanymawmhixyq:JLBeck33!@aws-0-ca-central-1.pooler.supabase.com:6543/postgres",
        env="DATABASE_URL"
    )
    
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
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
            raise ValueError('Database URL must start with postgresql:// or postgresql+asyncpg://')
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

# Create settings instance AFTER environment is loaded
_settings = None

def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
        print(f"Settings loaded: {_settings.model_dump()}")
    return _settings

def is_development() -> bool:
    """Check if running in development mode."""
    return get_settings().debug

def is_production() -> bool:
    """Check if running in production mode."""
    return not get_settings().debug
