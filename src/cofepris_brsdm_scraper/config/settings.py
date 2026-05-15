"""Application settings."""

from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Typed environment settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")
    portal_url: str = Field(
        default="https://tramiteselectronicos02.cofepris.gob.mx/BRSDM/default.aspx",
        alias="PORTAL_URL",
    )
    table_name: str = Field(default="medicamentos", alias="TABLE_NAME")
    scraper_retries: int = Field(default=3, alias="SCRAPER_RETRIES")
    scraper_timeout_ms: int = Field(default=30000, alias="SCRAPER_TIMEOUT_MS")
    scraper_backoff_seconds: float = Field(default=1.0, alias="SCRAPER_BACKOFF_SECONDS")
    scraper_stealth_enabled: bool = Field(default=True, alias="SCRAPER_STEALTH_ENABLED")
    scraper_headless: bool = Field(default=True, alias="SCRAPER_HEADLESS")
    scraper_user_agent: str = Field(
        default=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        alias="SCRAPER_USER_AGENT",
    )
    scraper_viewport_width: int = Field(default=1280, alias="SCRAPER_VIEWPORT_WIDTH")
    scraper_viewport_height: int = Field(default=720, alias="SCRAPER_VIEWPORT_HEIGHT")
    scraper_locale: str = Field(default="en-US", alias="SCRAPER_LOCALE")
    scraper_timezone_id: str = Field(default="America/Mexico_City", alias="SCRAPER_TIMEZONE_ID")
    scraper_proxy_servers: Annotated[tuple[str, ...], NoDecode] = Field(
        default=(), alias="SCRAPER_PROXY_SERVERS"
    )
    scraper_proxy_username: str | None = Field(default=None, alias="SCRAPER_PROXY_USERNAME")
    scraper_proxy_password: str | None = Field(default=None, alias="SCRAPER_PROXY_PASSWORD")
    scraper_proxy_v2_enabled: bool = Field(default=False, alias="SCRAPER_PROXY_V2_ENABLED")
    scraper_proxy_circuit_failure_threshold: int = Field(
        default=3, alias="SCRAPER_PROXY_CIRCUIT_FAILURE_THRESHOLD"
    )
    scraper_proxy_circuit_cooldown_seconds: int = Field(
        default=600, alias="SCRAPER_PROXY_CIRCUIT_COOLDOWN_SECONDS"
    )
    scraper_proxy_half_open_max_trials: int = Field(
        default=1, alias="SCRAPER_PROXY_HALF_OPEN_MAX_TRIALS"
    )
    scraper_proxy_sticky_ttl_seconds: int = Field(
        default=900, alias="SCRAPER_PROXY_STICKY_TTL_SECONDS"
    )
    scraper_proxy_health_decay_on_success: int = Field(
        default=1, alias="SCRAPER_PROXY_HEALTH_DECAY_ON_SUCCESS"
    )
    scraper_proxy_health_penalty_timeout: int = Field(
        default=1, alias="SCRAPER_PROXY_HEALTH_PENALTY_TIMEOUT"
    )
    scraper_proxy_health_penalty_block: int = Field(
        default=3, alias="SCRAPER_PROXY_HEALTH_PENALTY_BLOCK"
    )
    scraper_proxy_strategy_failopen: bool = Field(
        default=True, alias="SCRAPER_PROXY_STRATEGY_FAILOPEN"
    )
    load_chunk_size: int = Field(default=10000, alias="LOAD_CHUNK_SIZE")
    attempts_table_name: str = Field(default="scraping_attempts", alias="ATTEMPTS_TABLE_NAME")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    cron_expression: str = Field(default="0 6 * * *", alias="CRON_EXPRESSION")
    lock_path: str = Field(default="/tmp/cofepris-brsdm.lock", alias="LOCK_PATH")

    @field_validator("scraper_proxy_servers", mode="before")
    @classmethod
    def _parse_proxy_servers(cls, value: str | tuple[str, ...] | None) -> tuple[str, ...]:
        if value is None:
            return ()
        if isinstance(value, tuple):
            return value
        if isinstance(value, str):
            return tuple(item.strip() for item in value.split(",") if item.strip())
        raise TypeError("SCRAPER_PROXY_SERVERS must be a comma-separated string or tuple.")
