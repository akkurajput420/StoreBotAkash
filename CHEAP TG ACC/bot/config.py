from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(alias="BOT_TOKEN")
    api_id: int = Field(alias="API_ID")
    api_hash: str = Field(alias="API_HASH")
    owner_id: int = Field(alias="OWNER_ID")

    database_url: str = Field(default="sqlite:///bot_database.db", alias="DATABASE_URL")
    bot_session_name: str = Field(default="store_bot", alias="BOT_SESSION_NAME")
    sessions_dir: str = Field(default="MyTelethon", alias="SESSIONS_DIR")
    backup_dir: str = Field(default="backups", alias="BACKUP_DIR")

    broadcast_workers: int = Field(default=5, alias="BROADCAST_WORKERS")
    otp_listener_timeout: int = Field(default=900, alias="OTP_LISTENER_TIMEOUT")
    rate_limit_per_minute: int = Field(default=30, alias="RATE_LIMIT_PER_MINUTE")

    fampay_api_base_url: str = Field(default="http://payment.openosint.in/api/", alias="FAMPAY_API_BASE_URL")
    fampay_upi_id: str = Field(default="raresharmaji@fam", alias="FAMPAY_UPI_ID")
    payment_min_amount: float = Field(default=1.0, alias="PAYMENT_MIN_AMOUNT")
    payment_max_amount: float = Field(default=50000.0, alias="PAYMENT_MAX_AMOUNT")
    payment_poll_interval: int = Field(default=7, alias="PAYMENT_POLL_INTERVAL")
    payment_poll_timeout: int = Field(default=900, alias="PAYMENT_POLL_TIMEOUT")

    account_display_name: str = Field(default="TelegramAcc Seller Cheapest", alias="ACCOUNT_DISPLAY_NAME")
    account_bio: str = Field(default="@TgEliteStoreBot", alias="ACCOUNT_BIO")
    required_channel_link: str = Field(default="https://t.me/Tg_Buyer_Seller", alias="REQUIRED_CHANNEL_LINK")
    spambot_username: str = Field(default="SpamBot", alias="SPAMBOT_USERNAME")

    @property
    def sqlite_path(self) -> str:
        if self.database_url.startswith("sqlite:///"):
            return self.database_url.replace("sqlite:///", "", 1)
        return "bot_database.db"

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent


@lru_cache
def get_settings() -> Settings:
    return Settings()
