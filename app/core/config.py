"""Application configuration using Pydantic."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """Database configuration."""

    url: str = Field(..., alias="DATABASE_URL")
    echo: bool = Field(False, alias="DATABASE_ECHO")
    pool_size: int = Field(20, alias="DATABASE_POOL_SIZE")
    max_overflow: int = Field(0, alias="DATABASE_MAX_OVERFLOW")
    timeout: int = Field(30, alias="DATABASE_TIMEOUT")

    class Config:
        env_file = ".env"
        case_sensitive = False


class RedisConfig(BaseSettings):
    """Redis configuration."""

    url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    db: int = Field(default=0, alias="REDIS_DB")

    class Config:
        env_file = ".env"
        case_sensitive = False


class TelegramBotConfig(BaseSettings):
    """Telegram bot configuration."""

    token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    username: str = Field(..., alias="TELEGRAM_BOT_USERNAME")
    admin_ids: list[int] = Field(default_factory=list, alias="ADMIN_IDS")

    @validator("admin_ids", pre=True)
    def parse_admin_ids(cls, v: str | list) -> list[int]:
        """Parse admin IDs from comma-separated string."""
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


class TelethonConfig(BaseSettings):
    """Telethon configuration."""

    api_id: int = Field(..., alias="TELETHON_API_ID")
    api_hash: str = Field(..., alias="TELETHON_API_HASH")
    session_dir: str = Field(default="./sessions", alias="TELETHON_SESSION_DIR")

    class Config:
        env_file = ".env"
        case_sensitive = False


class CryptoBotConfig(BaseSettings):
    """CryptoBot payment configuration."""

    api_token: str = Field(..., alias="CRYPTOBOT_API_TOKEN")
    shop_id: str = Field(..., alias="CRYPTOBOT_SHOP_ID")
    webhook_secret: str = Field(..., alias="CRYPTOBOT_WEBHOOK_SECRET")
    api_url: str = Field(default="https://pay.crypt.bot/api", alias="CRYPTOBOT_API_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False


class TONConfig(BaseSettings):
    """TON Keeper payment configuration."""

    wallet_address: str = Field(..., alias="TON_WALLET_ADDRESS")
    mnemonic: Optional[str] = Field(default=None, alias="TON_MNEMONIC")
    rpc_endpoint: str = Field(default="https://testnet.toncenter.com/api/v2/jsonRPC", alias="TON_RPC_ENDPOINT")
    network: str = Field(default="testnet", alias="TON_NETWORK")
    watch_interval: int = Field(default=30, alias="TON_WATCH_INTERVAL")

    class Config:
        env_file = ".env"
        case_sensitive = False


class APIConfig(BaseSettings):
    """API configuration."""

    host: str = Field(default="0.0.0.0", alias="API_HOST")
    port: int = Field(default=8000, alias="API_PORT")
    workers: int = Field(default=4, alias="API_WORKERS")
    webhook_url: str = Field(..., alias="API_WEBHOOK_URL")
    webhook_secret: str = Field(..., alias="WEBHOOK_SECRET")
    webhook_timeout: int = Field(default=30, alias="WEBHOOK_TIMEOUT")

    class Config:
        env_file = ".env"
        case_sensitive = False


class SessionConfig(BaseSettings):
    """Session configuration."""

    encryption_key: str = Field(..., alias="SESSION_ENCRYPTION_KEY")

    @validator("encryption_key")
    def validate_encryption_key(cls, v: str) -> str:
        """Validate encryption key length."""
        if len(v) != 32:
            raise ValueError("Encryption key must be 32 characters long")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


class OrderConfig(BaseSettings):
    """Order configuration."""

    reservation_ttl: int = Field(default=3600, alias="ORDER_RESERVATION_TTL")
    payment_timeout: int = Field(default=1800, alias="ORDER_PAYMENT_TIMEOUT")
    auto_cancel_hours: int = Field(default=24, alias="AUTO_CANCEL_ORDER_HOURS")

    class Config:
        env_file = ".env"
        case_sensitive = False


class CleanupConfig(BaseSettings):
    """Cleanup configuration."""

    retry_interval: int = Field(default=1800, alias="CLEANUP_RETRY_INTERVAL")
    max_retries: int = Field(default=10, alias="CLEANUP_MAX_RETRIES")

    class Config:
        env_file = ".env"
        case_sensitive = False


class RateLimitConfig(BaseSettings):
    """Rate limiting configuration."""

    requests: int = Field(default=10, alias="RATE_LIMIT_REQUESTS")
    period: int = Field(default=60, alias="RATE_LIMIT_PERIOD")

    class Config:
        env_file = ".env"
        case_sensitive = False


class AntiSpamConfig(BaseSettings):
    """Anti-spam configuration."""

    flood_threshold: int = Field(default=5, alias="FLOOD_THRESHOLD")
    flood_block_duration: int = Field(default=600, alias="FLOOD_BLOCK_DURATION")

    class Config:
        env_file = ".env"
        case_sensitive = False


class LoggingConfig(BaseSettings):
    """Logging configuration."""

    level: str = Field(default="INFO", alias="LOG_LEVEL")
    format: str = Field(default="json", alias="LOG_FORMAT")
    file: str = Field(default="./logs/app.log", alias="LOG_FILE")

    class Config:
        env_file = ".env"
        case_sensitive = False


class Settings(BaseSettings):
    """Main application settings."""

    app_name: str = Field(default="telegram-accounts-marketplace", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="production", alias="ENVIRONMENT")

    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    telegram_bot: TelegramBotConfig = TelegramBotConfig()
    telethon: TelethonConfig = TelethonConfig()
    cryptobot: CryptoBotConfig = CryptoBotConfig()
    ton: TONConfig = TONConfig()
    api: APIConfig = APIConfig()
    session: SessionConfig = SessionConfig()
    order: OrderConfig = OrderConfig()
    cleanup: CleanupConfig = CleanupConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()
    anti_spam: AntiSpamConfig = AntiSpamConfig()
    logging: LoggingConfig = LoggingConfig()

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
