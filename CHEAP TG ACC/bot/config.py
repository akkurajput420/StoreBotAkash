from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, PositiveFloat, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # Core Telegram Configuration
    bot_token: str = Field(..., alias="BOT_TOKEN")
    api_id: int = Field(..., alias="API_ID")
    api_hash: str = Field(..., alias="API_HASH")
    owner_id: int = Field(..., alias="OWNER_ID")

    # Database & Storage
    database_url: str = Field(default="sqlite:///bot_database.db", alias="DATABASE_URL")
    bot_session_name: str = Field(default="store_bot", alias="BOT_SESSION_NAME")
    sessions_dir: Path = Field(default=Path("MyTelethon"), alias="SESSIONS_DIR")
    backup_dir: Path = Field(default=Path("backups"), alias="BACKUP_DIR")

    # Bot Limits & Timeouts
    broadcast_workers: PositiveInt = Field(default=5, alias="BROADCAST_WORKERS")
    otp_listener_timeout: PositiveInt = Field(default=900, alias="OTP_LISTENER_TIMEOUT")
    rate_limit_per_minute: PositiveInt = Field(default=30, alias="RATE_LIMIT_PER_MINUTE")

    # Payment Gateway Configuration (FamPay)
    fampay_api_base_url: str = Field(default="http://payment.openosint.in/api/", alias="FAMPAY_API_BASE_URL")
    fampay_upi_id: str = Field(default="raresharmaji@fam", alias="FAMPAY_UPI_ID")
    payment_min_amount: PositiveFloat = Field(default=1.0, alias="PAYMENT_MIN_AMOUNT")
    payment_max_amount: PositiveFloat = Field(default=50000.0, alias="PAYMENT_MAX_AMOUNT")
    payment_poll_interval: PositiveInt = Field(default=7, alias="PAYMENT_POLL_INTERVAL")
    payment_poll_timeout: PositiveInt = Field(default=900, alias="PAYMENT_POLL_TIMEOUT")

    # Store Branding & Info
    account_display_name: str = Field(default="TelegramAcc Seller Cheapest", alias="ACCOUNT_DISPLAY_NAME")
    account_bio: str = Field(default="@TgEliteStoreBot", alias="ACCOUNT_BIO")
    required_channel_link: str = Field(default="https://t.me/Tg_Buyer_Seller", alias="REQUIRED_CHANNEL_LINK")
    spambot_username: str = Field(default="SpamBot", alias="SPAMBOT_USERNAME")

    @property
    def sqlite_path(self) -> str:
        """Extract clean relative/absolute path from SQLite Database URL."""
        if "sqlite:///" in self.database_url:
            return self.database_url.split("sqlite:///", 1)[1]
        elif "sqlite://" in self.database_url:
            return self.database_url.split("sqlite://", 1)[1]
        return "bot_database.db"

    @property
    def project_root(self) -> Path:
        """Get the absolute root directory path of the project."""
        return Path(__file__).resolve().parent.parent

    def setup_directories(self) -> None:
        """Helper to safely create sessions and backups folders on launch."""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Singleton getter for cached configuration instance."""
    settings = Settings()
    settings.setup_directories()
    return settings
