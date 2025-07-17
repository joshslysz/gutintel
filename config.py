from typing import List, Optional, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig(BaseSettings):
    url: str = Field(..., alias="DATABASE_URL")
    min_connections: int = Field(5, alias="DATABASE_MIN_CONNECTIONS")
    max_connections: int = Field(20, alias="DATABASE_MAX_CONNECTIONS")
    max_retries: int = Field(3, alias="DATABASE_MAX_RETRIES")
    retry_delay: float = Field(1.0, alias="DATABASE_RETRY_DELAY")
    command_timeout: float = Field(30.0, alias="DATABASE_COMMAND_TIMEOUT")

    @field_validator("url")
    @classmethod
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("Database URL must be a valid PostgreSQL connection string")
        return v

    @field_validator("min_connections")
    @classmethod
    def validate_min_connections(cls, v):
        if v < 1:
            raise ValueError("Minimum connections must be at least 1")
        return v

    @field_validator("max_connections")
    @classmethod
    def validate_max_connections(cls, v, info):
        if v < info.data.get("min_connections", 1):
            raise ValueError("Maximum connections must be greater than minimum connections")
        return v


class APIConfig(BaseSettings):
    host: str = Field("127.0.0.1", env="API_HOST")
    port: int = Field(8000, env="API_PORT")
    reload: bool = Field(False, env="API_RELOAD")
    workers: int = Field(1, env="API_WORKERS")
    title: str = Field("GutIntel API", env="API_TITLE")
    version: str = Field("1.0.0", env="API_VERSION")
    prefix: str = Field("/api/v1", env="API_PREFIX")

    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("workers")
    @classmethod
    def validate_workers(cls, v):
        if v < 1:
            raise ValueError("Workers must be at least 1")
        return v


class SecurityConfig(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    algorithm: str = Field("HS256", env="ALGORITHM")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_access_token_expire(cls, v):
        if v < 1:
            raise ValueError("Access token expiration must be at least 1 minute")
        return v


class CORSConfig(BaseSettings):
    origins: List[str] = Field(["http://localhost:3000"], env="CORS_ORIGINS")
    credentials: bool = Field(True, env="CORS_CREDENTIALS")
    methods: List[str] = Field(["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="CORS_METHODS")
    headers: List[str] = Field(["*"], env="CORS_HEADERS")


class ExternalAPIConfig(BaseSettings):
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")


class LoggingConfig(BaseSettings):
    level: str = Field("INFO", env="LOG_LEVEL")
    format: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    file_path: str = Field("logs/gutintel.log", env="LOG_FILE_PATH")
    max_bytes: int = Field(10485760, env="LOG_MAX_BYTES")  # 10MB
    backup_count: int = Field(5, env="LOG_BACKUP_COUNT")

    @field_validator("level")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @field_validator("max_bytes")
    @classmethod
    def validate_max_bytes(cls, v):
        if v < 1024:  # 1KB minimum
            raise ValueError("Log file max bytes must be at least 1024 bytes")
        return v


class RateLimitConfig(BaseSettings):
    requests: int = Field(100, env="RATE_LIMIT_REQUESTS")
    window: int = Field(60, env="RATE_LIMIT_WINDOW")  # seconds

    @field_validator("requests")
    @classmethod
    def validate_requests(cls, v):
        if v < 1:
            raise ValueError("Rate limit requests must be at least 1")
        return v

    @field_validator("window")
    @classmethod
    def validate_window(cls, v):
        if v < 1:
            raise ValueError("Rate limit window must be at least 1 second")
        return v


class HealthCheckConfig(BaseSettings):
    interval: int = Field(30, env="HEALTH_CHECK_INTERVAL")  # seconds
    timeout: int = Field(10, env="HEALTH_CHECK_TIMEOUT")  # seconds

    @field_validator("interval")
    @classmethod
    def validate_interval(cls, v):
        if v < 1:
            raise ValueError("Health check interval must be at least 1 second")
        return v

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v):
        if v < 1:
            raise ValueError("Health check timeout must be at least 1 second")
        return v


class RedisConfig(BaseSettings):
    url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    ttl: int = Field(3600, env="REDIS_TTL")  # seconds

    @field_validator("ttl")
    @classmethod
    def validate_ttl(cls, v):
        if v < 1:
            raise ValueError("Redis TTL must be at least 1 second")
        return v


class EmailConfig(BaseSettings):
    smtp_host: str = Field("smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    from_email: str = Field("noreply@gutintel.com", env="SMTP_FROM_EMAIL")
    from_name: str = Field("GutIntel", env="SMTP_FROM_NAME")

    @field_validator("smtp_port")
    @classmethod
    def validate_smtp_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("SMTP port must be between 1 and 65535")
        return v


class FileUploadConfig(BaseSettings):
    max_size: int = Field(10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    directory: str = Field("uploads/", env="UPLOAD_DIRECTORY")
    allowed_extensions: List[str] = Field(["pdf", "txt", "docx", "csv", "json"], env="ALLOWED_EXTENSIONS")

    @field_validator("max_size")
    @classmethod
    def validate_max_size(cls, v):
        if v < 1024:  # 1KB minimum
            raise ValueError("Max upload size must be at least 1KB")
        return v

    @field_validator("directory")
    @classmethod
    def validate_directory(cls, v):
        if not v.endswith("/"):
            v += "/"
        # Create directory if it doesn't exist
        Path(v).mkdir(parents=True, exist_ok=True)
        return v


class MonitoringConfig(BaseSettings):
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    prometheus_metrics_port: int = Field(9090, env="PROMETHEUS_METRICS_PORT")
    jaeger_agent_host: str = Field("localhost", env="JAEGER_AGENT_HOST")
    jaeger_agent_port: int = Field(14268, env="JAEGER_AGENT_PORT")

    @field_validator("prometheus_metrics_port")
    @classmethod
    def validate_prometheus_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Prometheus metrics port must be between 1 and 65535")
        return v

    @field_validator("jaeger_agent_port")
    @classmethod
    def validate_jaeger_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Jaeger agent port must be between 1 and 65535")
        return v


class Settings(BaseSettings):
    environment: Literal["development", "staging", "production"] = Field("development", env="ENVIRONMENT")
    
    # Configuration sections will be populated lazily

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize configuration sections lazily
        self._database = None
        self._api = None
        self._security = None
        self._cors = None
        self._external_api = None
        self._logging = None
        self._rate_limit = None
        self._health_check = None
        self._redis = None
        self._email = None
        self._file_upload = None
        self._monitoring = None
        
        # Initialize logging directory
        log_dir = Path(self.logging.file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

    @property
    def database(self) -> DatabaseConfig:
        if self._database is None:
            self._database = DatabaseConfig()
        return self._database

    @property
    def api(self) -> APIConfig:
        if self._api is None:
            self._api = APIConfig()
        return self._api

    @property
    def security(self) -> SecurityConfig:
        if self._security is None:
            self._security = SecurityConfig()
        return self._security

    @property
    def cors(self) -> CORSConfig:
        if self._cors is None:
            self._cors = CORSConfig()
        return self._cors

    @property
    def external_api(self) -> ExternalAPIConfig:
        if self._external_api is None:
            self._external_api = ExternalAPIConfig()
        return self._external_api

    @property
    def logging(self) -> LoggingConfig:
        if self._logging is None:
            self._logging = LoggingConfig()
        return self._logging

    @property
    def rate_limit(self) -> RateLimitConfig:
        if self._rate_limit is None:
            self._rate_limit = RateLimitConfig()
        return self._rate_limit

    @property
    def health_check(self) -> HealthCheckConfig:
        if self._health_check is None:
            self._health_check = HealthCheckConfig()
        return self._health_check

    @property
    def redis(self) -> RedisConfig:
        if self._redis is None:
            self._redis = RedisConfig()
        return self._redis

    @property
    def email(self) -> EmailConfig:
        if self._email is None:
            self._email = EmailConfig()
        return self._email

    @property
    def file_upload(self) -> FileUploadConfig:
        if self._file_upload is None:
            self._file_upload = FileUploadConfig()
        return self._file_upload

    @property
    def monitoring(self) -> MonitoringConfig:
        if self._monitoring is None:
            self._monitoring = MonitoringConfig()
        return self._monitoring

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_staging(self) -> bool:
        return self.environment == "staging"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    def get_database_url(self) -> str:
        """Get the database URL for connection"""
        return self.database.url

    def get_api_url(self) -> str:
        """Get the full API URL"""
        return f"http://{self.api.host}:{self.api.port}{self.api.prefix}"

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins list"""
        return self.cors.origins

    def get_log_config(self) -> dict:
        """Get logging configuration dictionary"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.logging.format,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": self.logging.level,
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "default",
                    "filename": self.logging.file_path,
                    "maxBytes": self.logging.max_bytes,
                    "backupCount": self.logging.backup_count,
                    "level": self.logging.level,
                },
            },
            "root": {
                "level": self.logging.level,
                "handlers": ["console", "file"],
            },
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment variables"""
    global settings
    settings = Settings()
    return settings