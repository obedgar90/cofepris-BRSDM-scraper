"""Settings tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from cofepris_brsdm_scraper.config.settings import Settings


def test_settings_raise_validation_error_when_database_url_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Settings must fail without DATABASE_URL."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_include_stealth_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings should expose anti-bot defaults when env vars are omitted."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    monkeypatch.delenv("SCRAPER_STEALTH_ENABLED", raising=False)
    monkeypatch.delenv("SCRAPER_HEADLESS", raising=False)
    monkeypatch.delenv("SCRAPER_USER_AGENT", raising=False)
    monkeypatch.delenv("SCRAPER_VIEWPORT_WIDTH", raising=False)
    monkeypatch.delenv("SCRAPER_VIEWPORT_HEIGHT", raising=False)
    monkeypatch.delenv("SCRAPER_LOCALE", raising=False)
    monkeypatch.delenv("SCRAPER_TIMEZONE_ID", raising=False)
    monkeypatch.delenv("SCRAPER_PROXY_V2_ENABLED", raising=False)
    monkeypatch.delenv("SCRAPER_PROXY_CIRCUIT_FAILURE_THRESHOLD", raising=False)
    monkeypatch.delenv("SCRAPER_PROXY_CIRCUIT_COOLDOWN_SECONDS", raising=False)
    monkeypatch.delenv("SCRAPER_PROXY_HALF_OPEN_MAX_TRIALS", raising=False)
    monkeypatch.delenv("SCRAPER_PROXY_STICKY_TTL_SECONDS", raising=False)
    monkeypatch.delenv("SCRAPER_PROXY_HEALTH_DECAY_ON_SUCCESS", raising=False)
    monkeypatch.delenv("SCRAPER_PROXY_HEALTH_PENALTY_TIMEOUT", raising=False)
    monkeypatch.delenv("SCRAPER_PROXY_HEALTH_PENALTY_BLOCK", raising=False)
    monkeypatch.delenv("SCRAPER_PROXY_STRATEGY_FAILOPEN", raising=False)
    monkeypatch.delenv("ATTEMPTS_TABLE_NAME", raising=False)

    settings = Settings()

    assert settings.scraper_stealth_enabled is True
    assert settings.scraper_headless is True
    assert settings.scraper_user_agent
    assert settings.scraper_viewport_width == 1280
    assert settings.scraper_viewport_height == 720
    assert settings.scraper_locale == "en-US"
    assert settings.scraper_timezone_id == "America/Mexico_City"
    assert settings.scraper_proxy_v2_enabled is False
    assert settings.scraper_proxy_circuit_failure_threshold == 3
    assert settings.scraper_proxy_circuit_cooldown_seconds == 600
    assert settings.scraper_proxy_half_open_max_trials == 1
    assert settings.scraper_proxy_sticky_ttl_seconds == 900
    assert settings.scraper_proxy_health_decay_on_success == 1
    assert settings.scraper_proxy_health_penalty_timeout == 1
    assert settings.scraper_proxy_health_penalty_block == 3
    assert settings.scraper_proxy_strategy_failopen is True
    assert settings.attempts_table_name == "scraping_attempts"


def test_settings_parse_proxy_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings should parse proxy server list and optional credentials from env."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    monkeypatch.setenv("SCRAPER_PROXY_SERVERS", "http://p1:8000, http://p2:8001")
    monkeypatch.setenv("SCRAPER_PROXY_USERNAME", "proxy-user")
    monkeypatch.setenv("SCRAPER_PROXY_PASSWORD", "proxy-pass")

    settings = Settings()

    assert settings.scraper_proxy_servers == ("http://p1:8000", "http://p2:8001")
    assert settings.scraper_proxy_username == "proxy-user"
    assert settings.scraper_proxy_password == "proxy-pass"


def test_settings_parse_proxy_v2_thresholds(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings should parse V2 proxy strategy thresholds from environment."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    monkeypatch.setenv("SCRAPER_PROXY_V2_ENABLED", "true")
    monkeypatch.setenv("SCRAPER_PROXY_CIRCUIT_FAILURE_THRESHOLD", "5")
    monkeypatch.setenv("SCRAPER_PROXY_CIRCUIT_COOLDOWN_SECONDS", "1200")
    monkeypatch.setenv("SCRAPER_PROXY_HALF_OPEN_MAX_TRIALS", "2")
    monkeypatch.setenv("SCRAPER_PROXY_STICKY_TTL_SECONDS", "1800")
    monkeypatch.setenv("SCRAPER_PROXY_HEALTH_DECAY_ON_SUCCESS", "2")
    monkeypatch.setenv("SCRAPER_PROXY_HEALTH_PENALTY_TIMEOUT", "2")
    monkeypatch.setenv("SCRAPER_PROXY_HEALTH_PENALTY_BLOCK", "6")
    monkeypatch.setenv("SCRAPER_PROXY_STRATEGY_FAILOPEN", "false")

    settings = Settings()

    assert settings.scraper_proxy_v2_enabled is True
    assert settings.scraper_proxy_circuit_failure_threshold == 5
    assert settings.scraper_proxy_circuit_cooldown_seconds == 1200
    assert settings.scraper_proxy_half_open_max_trials == 2
    assert settings.scraper_proxy_sticky_ttl_seconds == 1800
    assert settings.scraper_proxy_health_decay_on_success == 2
    assert settings.scraper_proxy_health_penalty_timeout == 2
    assert settings.scraper_proxy_health_penalty_block == 6
    assert settings.scraper_proxy_strategy_failopen is False
