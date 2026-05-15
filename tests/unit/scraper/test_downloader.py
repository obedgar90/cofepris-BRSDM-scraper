"""Downloader unit tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from cofepris_brsdm_scraper.exceptions import (
    BotBlockedError,
    DownloadError,
    PortalUIChangedError,
)
from cofepris_brsdm_scraper.scraper.downloader import Downloader


class FakeProxyStrategy:
    """Proxy strategy spy for downloader integration tests."""

    def __init__(self) -> None:
        self.select_calls: list[str] = []
        self.report_calls: list[tuple[str, str, str]] = []

    def select_proxy(self, domain: str) -> dict[str, str]:
        self.select_calls.append(domain)
        return {"server": "http://strategy-proxy:8080", "username": "usr", "password": "pwd"}

    def report_outcome(self, *, domain: str, proxy_server: str, outcome: str) -> None:
        self.report_calls.append((domain, proxy_server, outcome))


def test_downloader_retries_transient_timeout_and_succeeds(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Downloader should retry timeout failures and then return file."""
    attempts = {"count": 0}

    def fake_download_once(self: Downloader, output_dir: Path) -> Path:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise PlaywrightTimeoutError("timeout")
        file_path = output_dir / "ok.xlsx"
        file_path.write_text("ok", encoding="utf-8")
        return file_path

    monkeypatch.setattr(Downloader, "_download_once", fake_download_once)
    downloader = Downloader("https://example.com", retries=3, backoff_seconds=0.0)

    result = downloader.download(tmp_path)
    assert result.name == "ok.xlsx"
    assert attempts["count"] == 3


def test_downloader_uses_proxy_strategy_selection_for_launch_options() -> None:
    """Downloader should use V2 strategy-selected proxy when enabled."""
    strategy = FakeProxyStrategy()
    downloader = Downloader(
        "https://tramiteselectronicos02.cofepris.gob.mx/BRSDM/default.aspx",
        proxy_strategy=strategy,
        proxy_v2_enabled=True,
    )

    launch_options = downloader._build_launch_options(attempt=1)

    assert launch_options["proxy"]["server"] == "http://strategy-proxy:8080"
    assert strategy.select_calls == ["tramiteselectronicos02.cofepris.gob.mx"]


def test_downloader_reports_outcome_to_proxy_strategy(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Downloader should report attempt outcome back to proxy strategy."""
    strategy = FakeProxyStrategy()

    def fake_download_once(self: Downloader, output_dir: Path) -> Path:
        self._active_proxy_server = "http://strategy-proxy:8080"
        file_path = output_dir / "ok.xlsx"
        file_path.write_text("ok", encoding="utf-8")
        return file_path

    monkeypatch.setattr(Downloader, "_download_once", fake_download_once)
    downloader = Downloader(
        "https://tramiteselectronicos02.cofepris.gob.mx/BRSDM/default.aspx",
        proxy_strategy=strategy,
        proxy_v2_enabled=True,
        retries=1,
    )

    downloader.download(tmp_path)

    assert strategy.report_calls == [
        ("tramiteselectronicos02.cofepris.gob.mx", "http://strategy-proxy:8080", "success")
    ]


def test_downloader_raises_download_error_after_exhausting_retries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Downloader should raise DownloadError after retry exhaustion."""

    def always_timeout(self: Downloader, output_dir: Path) -> Path:
        raise PlaywrightTimeoutError("timeout")

    monkeypatch.setattr(Downloader, "_download_once", always_timeout)
    downloader = Downloader("https://example.com", retries=2, backoff_seconds=0.0)

    with pytest.raises(DownloadError):
        downloader.download(tmp_path)


def test_downloader_does_not_retry_when_portal_ui_changed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """PortalUIChangedError should fail fast without retries."""

    def ui_changed(self: Downloader, output_dir: Path) -> Path:
        raise PortalUIChangedError("missing selector")

    monkeypatch.setattr(Downloader, "_download_once", ui_changed)
    downloader = Downloader("https://example.com", retries=3, backoff_seconds=0.0)

    with pytest.raises(PortalUIChangedError):
        downloader.download(tmp_path)


def test_downloader_builds_fortified_launch_options() -> None:
    """Downloader should include anti-bot hardening flags for Chromium launch."""
    downloader = Downloader(
        "https://example.com",
        stealth_enabled=True,
        headless=False,
        proxy_servers=(),
    )

    launch_options = downloader._build_launch_options(attempt=1)

    assert launch_options["headless"] is False
    assert "--disable-blink-features=AutomationControlled" in launch_options["args"]
    assert "--enable-webgl" in launch_options["args"]
    assert "--disable-infobars" in launch_options["args"]
    assert "proxy" not in launch_options


def test_downloader_builds_realistic_context_options() -> None:
    """Downloader should build realistic browser context settings."""
    downloader = Downloader(
        "https://example.com",
        stealth_enabled=True,
        user_agent="UA-TEST",
        viewport_width=1366,
        viewport_height=768,
        locale="en-US",
        timezone_id="America/Mexico_City",
        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
    )

    context_options = downloader._build_context_options()

    assert context_options["user_agent"] == "UA-TEST"
    assert context_options["viewport"] == {"width": 1366, "height": 768}
    assert context_options["locale"] == "en-US"
    assert context_options["timezone_id"] == "America/Mexico_City"
    assert context_options["extra_http_headers"]["Accept-Language"] == "en-US,en;q=0.9"


def test_downloader_rotates_proxy_by_attempt() -> None:
    """Downloader should rotate configured proxy endpoints across attempts."""
    downloader = Downloader(
        "https://example.com",
        proxy_servers=("http://proxy-a:8080", "http://proxy-b:8080"),
        proxy_username="u",
        proxy_password="p",
    )

    first = downloader._select_proxy_for_attempt(attempt=1)
    second = downloader._select_proxy_for_attempt(attempt=2)
    third = downloader._select_proxy_for_attempt(attempt=3)

    assert first == {"server": "http://proxy-a:8080", "username": "u", "password": "p"}
    assert second == {"server": "http://proxy-b:8080", "username": "u", "password": "p"}
    assert third == {"server": "http://proxy-a:8080", "username": "u", "password": "p"}


def test_downloader_retries_when_bot_block_detected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Bot-block errors should be treated as transient and retried."""
    attempts = {"count": 0}

    def fail_with_bot_block(self: Downloader, output_dir: Path) -> Path:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise BotBlockedError("captcha detected")
        file_path = output_dir / "ok.xlsx"
        file_path.write_text("ok", encoding="utf-8")
        return file_path

    monkeypatch.setattr(Downloader, "_download_once", fail_with_bot_block)
    downloader = Downloader("https://example.com", retries=3, backoff_seconds=0.0)

    result = downloader.download(tmp_path)

    assert result.name == "ok.xlsx"
    assert attempts["count"] == 3
