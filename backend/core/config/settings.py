"""
Project: AlphaQuant AI
File: backend/core/config/settings.py
Description: Centralized production settings for the AlphaQuant AI backend.
Python Version: 3.11.9
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import (
    AnyUrl,
    AnyHttpUrl,
    Field,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    """Supported application runtime environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    """Supported logging levels for Loguru."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AIProviderName(StrEnum):
    """Supported large language model providers."""

    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    QWEN = "qwen"
    KIMI = "kimi"


class StockProviderName(StrEnum):
    """Supported stock market data providers."""

    AKSHARE = "akshare"
    TUSHARE = "tushare"
    BAOSTOCK = "baostock"
    EASTMONEY = "eastmoney"
    SINA = "sina"
    TENCENT = "tencent"


class DatabaseEngine(StrEnum):
    """Database engines supported by the repository layer."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class BaseAppSettings(BaseSettings):
    """Base settings with shared environment file behavior."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class ServerSettings(BaseAppSettings):
    """HTTP server and OpenAPI settings."""

    app_name: str = Field(default="AlphaQuant AI", min_length=1)
    app_version: str = Field(default="0.1.0", min_length=1)
    environment: AppEnvironment = Field(default=AppEnvironment.DEVELOPMENT)
    debug: bool = Field(default=False)
    api_prefix: str = Field(default="/api/v1", pattern=r"^/[a-zA-Z0-9/_-]*$")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=2, ge=1, le=32)
    openapi_url: str | None = Field(default="/openapi.json")
    docs_url: str | None = Field(default="/docs")
    redoc_url: str | None = Field(default="/redoc")
    timezone: str = Field(default="Asia/Shanghai", min_length=1)

    @model_validator(mode="after")
    def disable_public_docs_in_production(self) -> ServerSettings:
        """Disable public API documentation when production hardening is active."""
        if self.environment == AppEnvironment.PRODUCTION and not self.debug:
            self.docs_url = None
            self.redoc_url = None
        return self


class SecuritySettings(BaseAppSettings):
    """Authentication, authorization, CORS, CSRF, and rate-limit settings."""

    jwt_secret_key: SecretStr = Field(
        default=SecretStr("change-me-with-a-strong-random-secret"),
        min_length=32,
    )
    jwt_algorithm: Literal["HS256", "HS384", "HS512", "RS256"] = Field(
        default="HS256",
    )
    access_token_expire_minutes: int = Field(default=60, ge=5, le=1440)
    refresh_token_expire_minutes: int = Field(default=60 * 24 * 14, ge=60)
    password_hash_algorithm: Literal["bcrypt"] = Field(default="bcrypt")
    password_bcrypt_rounds: int = Field(default=12, ge=10, le=16)
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"],
    )
    cors_allowed_methods: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    cors_allowed_headers: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = Field(default=True)
    csrf_enabled: bool = Field(default=True)
    csrf_cookie_name: str = Field(default="aq_csrf_token", min_length=1)
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=120, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: Any) -> list[str]:
        """Parse comma-separated CORS origins from environment variables."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return value
        raise ValueError("cors_allowed_origins must be a list or comma-separated string")

    @model_validator(mode="after")
    def validate_production_secret(self) -> SecuritySettings:
        """Reject insecure default secrets for non-development environments."""
        default_secret = "change-me-with-a-strong-random-secret"
        environment = getattr(self, "environment", AppEnvironment.DEVELOPMENT)
        if (
            environment != AppEnvironment.DEVELOPMENT
            and self.jwt_secret_key.get_secret_value() == default_secret
        ):
            message = "jwt_secret_key must be changed outside development"
            raise ValueError(message)
        return self


class DatabaseSettings(BaseAppSettings):
    """Database connection and SQLAlchemy pool settings."""

    database_engine: DatabaseEngine = Field(default=DatabaseEngine.POSTGRESQL)
    database_url: str = Field(
        default="sqlite+aiosqlite:////tmp/alphaquant.db",
    )
    database_echo: bool = Field(default=False)
    database_pool_size: int = Field(default=10, ge=1, le=100)
    database_max_overflow: int = Field(default=20, ge=0, le=200)
    database_pool_timeout_seconds: int = Field(default=30, ge=1, le=300)
    database_pool_recycle_seconds: int = Field(default=1800, ge=60)
    database_statement_timeout_ms: int = Field(default=30000, ge=1000)
    alembic_config_path: Path = Field(default=Path("backend/alembic.ini"))

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, value: Any) -> str:
        """Validate that a database URL is present and usable."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("database_url must be a non-empty string")
        return value.strip()


class RedisSettings(BaseAppSettings):
    """Redis connection, cache, broker, and result backend settings."""

    redis_url: RedisDsn | str = Field(default="redis://localhost:6379/0")
    redis_cache_db: int = Field(default=0, ge=0, le=15)
    redis_broker_db: int = Field(default=1, ge=0, le=15)
    redis_result_backend_db: int = Field(default=2, ge=0, le=15)
    redis_socket_timeout_seconds: float = Field(default=5.0, gt=0)
    redis_health_check_interval_seconds: int = Field(default=30, ge=1)
    cache_default_ttl_seconds: int = Field(default=300, ge=1)
    quote_cache_ttl_seconds: int = Field(default=5, ge=1)
    kline_cache_ttl_seconds: int = Field(default=300, ge=1)
    finance_cache_ttl_seconds: int = Field(default=3600, ge=60)
    news_cache_ttl_seconds: int = Field(default=600, ge=60)
    announcement_cache_ttl_seconds: int = Field(default=1800, ge=60)
    ai_analysis_cache_ttl_seconds: int = Field(default=3600, ge=60)

    @field_validator("redis_url", mode="before")
    @classmethod
    def validate_redis_url(cls, value: Any) -> str:
        """Validate that a Redis URL is present and usable."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("redis_url must be a non-empty string")
        return value.strip()


class LogSettings(BaseAppSettings):
    """Loguru file and console logging settings."""

    log_level: LogLevel = Field(default=LogLevel.INFO)
    log_dir: Path = Field(default=Path("logs"))
    log_file_name: str = Field(default="alphaquant-ai.log", min_length=1)
    log_rotation: str = Field(default="00:00")
    log_retention_days: int = Field(default=30, ge=1)
    log_compression: Literal["zip", "gz", "bz2", "xz", "tar"] | None = Field(
        default="zip",
    )
    log_enqueue: bool = Field(default=True)
    log_backtrace: bool = Field(default=False)
    log_diagnose: bool = Field(default=False)

    @property
    def log_file_path(self) -> Path:
        """Return the absolute or relative path used by the rotating file sink."""
        return self.log_dir / self.log_file_name


class AISettings(BaseAppSettings):
    """Unified AI provider settings for dynamic provider switching."""

    ai_default_provider: AIProviderName = Field(default=AIProviderName.DEEPSEEK)
    ai_enabled_providers: list[AIProviderName] = Field(
        default_factory=lambda: [AIProviderName.DEEPSEEK],
    )
    ai_request_timeout_seconds: float = Field(default=60.0, gt=0)
    ai_max_retries: int = Field(default=3, ge=0, le=10)
    ai_retry_backoff_seconds: float = Field(default=1.5, gt=0)
    ai_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    ai_max_tokens: int = Field(default=4096, ge=256)
    ai_analysis_model: str = Field(default="deepseek-chat", min_length=1)
    deepseek_api_key: SecretStr | None = Field(default=None)
    deepseek_base_url: AnyHttpUrl = Field(default="https://api.deepseek.com")
    openai_api_key: SecretStr | None = Field(default=None)
    openai_base_url: AnyHttpUrl = Field(default="https://api.openai.com/v1")
    claude_api_key: SecretStr | None = Field(default=None)
    claude_base_url: AnyHttpUrl = Field(default="https://api.anthropic.com")
    gemini_api_key: SecretStr | None = Field(default=None)
    gemini_base_url: AnyHttpUrl = Field(
        default="https://generativelanguage.googleapis.com",
    )
    qwen_api_key: SecretStr | None = Field(default=None)
    qwen_base_url: AnyHttpUrl = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    kimi_api_key: SecretStr | None = Field(default=None)
    kimi_base_url: AnyHttpUrl = Field(default="https://api.moonshot.cn/v1")

    @field_validator("ai_enabled_providers", mode="before")
    @classmethod
    def parse_enabled_providers(cls, value: Any) -> list[AIProviderName]:
        """Parse enabled AI providers from comma-separated environment variables."""
        if isinstance(value, str):
            return [
                AIProviderName(item.strip())
                for item in value.split(",")
                if item.strip()
            ]
        if isinstance(value, list):
            return value
        raise ValueError("ai_enabled_providers must be a list or comma-separated string")

    @model_validator(mode="after")
    def validate_default_provider_enabled(self) -> AISettings:
        """Ensure the default AI provider participates in provider routing."""
        if self.ai_default_provider not in self.ai_enabled_providers:
            message = "ai_default_provider must be included in ai_enabled_providers"
            raise ValueError(message)
        return self


class StockDataSettings(BaseAppSettings):
    """Unified stock data provider, retry, limit, and cache settings."""

    stock_default_market: Literal["A", "HK", "US"] = Field(default="A")
    stock_default_provider: StockProviderName = Field(default=StockProviderName.AKSHARE)
    stock_provider_priority: list[StockProviderName] = Field(
        default_factory=lambda: [
            StockProviderName.AKSHARE,
            StockProviderName.EASTMONEY,
            StockProviderName.SINA,
            StockProviderName.TENCENT,
            StockProviderName.TUSHARE,
            StockProviderName.BAOSTOCK,
        ],
    )
    stock_request_timeout_seconds: float = Field(default=15.0, gt=0)
    stock_max_retries: int = Field(default=3, ge=0, le=10)
    stock_retry_backoff_seconds: float = Field(default=1.0, gt=0)
    stock_rate_limit_per_minute: int = Field(default=120, ge=1)
    stock_market_open_time: str = Field(default="09:30")
    stock_market_close_time: str = Field(default="15:00")
    tushare_token: SecretStr | None = Field(default=None)
    alpha_vantage_api_key: SecretStr | None = Field(default=None)
    eastmoney_base_url: AnyHttpUrl = Field(default="https://push2.eastmoney.com")
    sina_base_url: AnyHttpUrl = Field(default="https://hq.sinajs.cn")
    tencent_base_url: AnyHttpUrl = Field(default="https://qt.gtimg.cn")

    @field_validator("stock_provider_priority", mode="before")
    @classmethod
    def parse_provider_priority(cls, value: Any) -> list[StockProviderName]:
        """Parse provider priority from comma-separated environment variables."""
        if isinstance(value, str):
            return [
                StockProviderName(item.strip())
                for item in value.split(",")
                if item.strip()
            ]
        if isinstance(value, list):
            return value
        raise ValueError("stock_provider_priority must be a list or comma-separated string")

    @model_validator(mode="after")
    def validate_default_provider_priority(self) -> StockDataSettings:
        """Ensure the default stock provider is present in failover priority."""
        if self.stock_default_provider not in self.stock_provider_priority:
            message = "stock_default_provider must be included in stock_provider_priority"
            raise ValueError(message)
        return self


class CelerySettings(BaseAppSettings):
    """Celery worker, broker, and scheduled task settings."""

    celery_app_name: str = Field(default="alphaquant_ai", min_length=1)
    celery_broker_url: RedisDsn | str = Field(default="redis://localhost:6379/1")
    celery_result_backend: RedisDsn | str = Field(default="redis://localhost:6379/2")
    celery_task_serializer: Literal["json"] = Field(default="json")
    celery_result_serializer: Literal["json"] = Field(default="json")
    celery_accept_content: list[Literal["json"]] = Field(default_factory=lambda: ["json"])
    celery_timezone: str = Field(default="Asia/Shanghai", min_length=1)
    celery_enable_utc: bool = Field(default=False)
    celery_task_time_limit_seconds: int = Field(default=300, ge=30)
    celery_task_soft_time_limit_seconds: int = Field(default=240, ge=30)
    celery_worker_prefetch_multiplier: int = Field(default=1, ge=1)


class SchedulerSettings(BaseAppSettings):
    """APScheduler settings for periodic market data and analysis jobs."""

    scheduler_enabled: bool = Field(default=True)
    scheduler_timezone: str = Field(default="Asia/Shanghai", min_length=1)
    quote_refresh_interval_seconds: int = Field(default=5, ge=1)
    kline_refresh_cron: str = Field(default="0 18 * * 1-5", min_length=1)
    finance_refresh_cron: str = Field(default="0 2 * * 6", min_length=1)
    news_refresh_interval_seconds: int = Field(default=600, ge=60)
    announcement_refresh_interval_seconds: int = Field(default=1800, ge=60)


class WebSocketSettings(BaseAppSettings):
    """WebSocket settings for realtime quotes, alerts, and dashboards."""

    websocket_enabled: bool = Field(default=True)
    websocket_path: str = Field(default="/ws", pattern=r"^/[a-zA-Z0-9/_-]*$")
    websocket_heartbeat_seconds: int = Field(default=30, ge=5)
    websocket_max_connections: int = Field(default=5000, ge=1)
    websocket_message_queue_size: int = Field(default=1000, ge=1)


class Settings(
    ServerSettings,
    SecuritySettings,
    DatabaseSettings,
    RedisSettings,
    LogSettings,
    AISettings,
    StockDataSettings,
    CelerySettings,
    SchedulerSettings,
    WebSocketSettings,
):
    """Complete application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
    )

    project_root: Path = Field(default=Path(__file__).resolve().parents[3])
    static_dir: Path = Field(default=Path("static"))
    upload_dir: Path = Field(default=Path("uploads"))
    max_upload_size_mb: int = Field(default=20, ge=1, le=1024)

    @model_validator(mode="after")
    def validate_environment_security(self) -> Settings:
        """Apply environment-aware security validation."""
        default_secret = "change-me-with-a-strong-random-secret"
        insecure_secret = self.jwt_secret_key.get_secret_value() == default_secret
        if self.environment != AppEnvironment.DEVELOPMENT and insecure_secret:
            message = "jwt_secret_key must be configured for non-development environments"
            raise ValueError(message)
        if self.environment == AppEnvironment.PRODUCTION and self.debug:
            message = "debug must be disabled in production"
            raise ValueError(message)
        return self

    @property
    def is_development(self) -> bool:
        """Return whether the application is running in development mode."""
        return self.environment == AppEnvironment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """Return whether the application is running in testing mode."""
        return self.environment == AppEnvironment.TESTING

    @property
    def is_production(self) -> bool:
        """Return whether the application is running in production mode."""
        return self.environment == AppEnvironment.PRODUCTION

    @property
    def sqlalchemy_database_url(self) -> str:
        """Return the database URL as a plain string for SQLAlchemy."""
        return str(self.database_url)

    @property
    def redis_cache_url(self) -> str:
        """Return the Redis cache URL as a plain string."""
        return str(self.redis_url)

    @property
    def celery_config(self) -> dict[str, Any]:
        """Return Celery-compatible configuration values."""
        return {
            "broker_url": str(self.celery_broker_url),
            "result_backend": str(self.celery_result_backend),
            "task_serializer": self.celery_task_serializer,
            "result_serializer": self.celery_result_serializer,
            "accept_content": self.celery_accept_content,
            "timezone": self.celery_timezone,
            "enable_utc": self.celery_enable_utc,
            "task_time_limit": self.celery_task_time_limit_seconds,
            "task_soft_time_limit": self.celery_task_soft_time_limit_seconds,
            "worker_prefetch_multiplier": self.celery_worker_prefetch_multiplier,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings loaded from environment variables."""
    return Settings()


settings = get_settings()
