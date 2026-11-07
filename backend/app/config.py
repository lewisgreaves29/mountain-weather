from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="production", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    poll_interval_minutes: int = Field(default=30, alias="POLL_INTERVAL_MINUTES")
    port: int = Field(default=8000, alias="PORT")
    host: str = Field(default="0.0.0.0", alias="HOST")

    # Path to locations configuration
    locations_file: Path = Field(
        default=Path("config/locations.yaml"),
        alias="LOCATIONS_FILE",
    )

    # 1Password injected secrets - mandatory, no default fallback
    auth_secret_token: str = Field(..., alias="AUTH_SECRET_TOKEN")
    alert_webhook_url: Optional[str] = Field(default=None, alias="ALERT_WEBHOOK_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()  # type: ignore[call-arg]
    except Exception as exc:
        raise RuntimeError(
            f"Configuration error: Missing required environment variable or secret. {exc}"
        ) from exc
