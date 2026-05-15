"""Playwright-based downloader for COFEPRIS BRSDM portal."""

from __future__ import annotations

import random
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from cofepris_brsdm_scraper.exceptions import (
    BotBlockedError,
    DownloadError,
    PortalUIChangedError,
)
from cofepris_brsdm_scraper.scraper.selectors import (
    COMPLETE_OPTION_VALUE,
    DOWNLOAD_BUTTON_ROLE_NAME,
    DROPDOWN_SELECTOR,
)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_CHALLENGE_MARKERS = (
    "captcha",
    "access denied",
    "verify you are human",
    "attention required",
    "temporarily blocked",
    "cloudflare",
)


class Downloader:
    """Download BRSDM complete XLSX from COFEPRIS portal."""

    def __init__(
        self,
        portal_url: str,
        retries: int = 3,
        timeout_ms: int = 30000,
        backoff_seconds: float = 1.0,
        stealth_enabled: bool = True,
        headless: bool = True,
        user_agent: str = DEFAULT_USER_AGENT,
        viewport_width: int = 1280,
        viewport_height: int = 720,
        locale: str = "en-US",
        timezone_id: str = "America/Mexico_City",
        extra_http_headers: dict[str, str] | None = None,
        proxy_servers: tuple[str, ...] = (),
        proxy_username: str | None = None,
        proxy_password: str | None = None,
        proxy_strategy: Any | None = None,
        proxy_v2_enabled: bool = False,
        proxy_strategy_failopen: bool = True,
        human_min_delay_ms: int = 80,
        human_max_delay_ms: int = 220,
        challenge_markers: tuple[str, ...] = DEFAULT_CHALLENGE_MARKERS,
    ) -> None:
        self._portal_url = portal_url
        self._retries = retries
        self._timeout_ms = timeout_ms
        self._backoff_seconds = backoff_seconds
        self._stealth_enabled = stealth_enabled
        self._headless = headless
        self._user_agent = user_agent
        self._viewport_width = viewport_width
        self._viewport_height = viewport_height
        self._locale = locale
        self._timezone_id = timezone_id
        self._extra_http_headers = extra_http_headers or {}
        self._proxy_servers = proxy_servers
        self._proxy_username = proxy_username
        self._proxy_password = proxy_password
        self._proxy_strategy = proxy_strategy
        self._proxy_v2_enabled = proxy_v2_enabled
        self._proxy_strategy_failopen = proxy_strategy_failopen
        self._human_min_delay_ms = human_min_delay_ms
        self._human_max_delay_ms = human_max_delay_ms
        self._challenge_markers = tuple(marker.lower() for marker in challenge_markers)
        self._active_attempt = 1
        self._active_proxy_server: str | None = None

    def download(self, output_dir: Path) -> Path:
        """Download the registry XLSX file with retry/backoff."""
        output_dir.mkdir(parents=True, exist_ok=True)
        last_error: Exception | None = None

        for attempt in range(1, self._retries + 1):
            try:
                self._active_attempt = attempt
                path = self._download_once(output_dir)
                self._report_proxy_outcome("success")
                return path
            except PortalUIChangedError:
                self._report_proxy_outcome("ui_changed")
                raise
            except BotBlockedError as exc:
                self._report_proxy_outcome("bot_blocked")
                last_error = exc
                if attempt < self._retries:
                    time.sleep(self._backoff_seconds * (2 ** (attempt - 1)))
            except PlaywrightTimeoutError as exc:
                self._report_proxy_outcome("transient_failure")
                last_error = exc
                if attempt < self._retries:
                    time.sleep(self._backoff_seconds * (2 ** (attempt - 1)))
            except Exception as exc:  # noqa: BLE001
                self._report_proxy_outcome("transient_failure")
                last_error = exc
                if attempt < self._retries:
                    time.sleep(self._backoff_seconds * (2 ** (attempt - 1)))

        raise DownloadError(
            f"Unable to download file after {self._retries} attempts."
        ) from last_error

    def _download_once(self, output_dir: Path) -> Path:
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
        destination = output_dir / f"cofepris-completo-{timestamp}.xlsx"

        launch_options = self._build_launch_options(attempt=self._active_attempt)
        context_options = self._build_context_options()

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**launch_options)
            context = browser.new_context(**context_options)
            page = context.new_page()
            try:
                if self._stealth_enabled:
                    page.add_init_script(self._stealth_init_script())
                page.goto(self._portal_url, wait_until="domcontentloaded", timeout=self._timeout_ms)
                self._raise_if_bot_blocked(page)
                self._validate_controls(page)
                self._simulate_human_jitter(page)
                page.locator(DROPDOWN_SELECTOR).select_option(COMPLETE_OPTION_VALUE)
                with page.expect_download(timeout=self._timeout_ms) as download_info:
                    self._simulate_human_jitter(page)
                    page.get_by_role("button", name=DOWNLOAD_BUTTON_ROLE_NAME).click()
                download = download_info.value
                download.save_as(str(destination))
            finally:
                context.close()
                browser.close()

        return destination

    def _validate_controls(self, page: Any) -> None:
        try:
            page.locator(DROPDOWN_SELECTOR).wait_for(state="visible", timeout=self._timeout_ms)
            page.locator(DROPDOWN_SELECTOR).select_option(COMPLETE_OPTION_VALUE)
        except Exception as exc:  # noqa: BLE001
            raise PortalUIChangedError(
                "Portal control not found or expected option value changed."
            ) from exc

    def _build_launch_options(self, attempt: int) -> dict[str, Any]:
        args = ["--disable-dev-shm-usage"]
        if self._stealth_enabled:
            args.extend(
                [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                    "--disable-infobars",
                    "--no-first-run",
                    "--enable-webgl",
                    "--enable-accelerated-2d-canvas",
                ]
            )
        options: dict[str, Any] = {"headless": self._headless, "args": args}
        proxy = self._select_proxy_for_attempt(attempt=attempt)
        if proxy:
            options["proxy"] = proxy
            self._active_proxy_server = proxy["server"]
        else:
            self._active_proxy_server = None
        return options

    def _build_context_options(self) -> dict[str, Any]:
        extra_headers = {"Accept-Language": self._locale}
        extra_headers.update(self._extra_http_headers)
        return {
            "accept_downloads": True,
            "user_agent": self._user_agent,
            "viewport": {
                "width": self._viewport_width,
                "height": self._viewport_height,
            },
            "locale": self._locale,
            "timezone_id": self._timezone_id,
            "extra_http_headers": extra_headers,
        }

    def _select_proxy_for_attempt(self, attempt: int) -> dict[str, str] | None:
        if self._proxy_v2_enabled and self._proxy_strategy is not None:
            try:
                domain = self._target_domain()
                return self._proxy_strategy.select_proxy(domain)
            except Exception:
                if not self._proxy_strategy_failopen:
                    raise
        if not self._proxy_servers:
            return None
        index = (attempt - 1) % len(self._proxy_servers)
        proxy: dict[str, str] = {"server": self._proxy_servers[index]}
        if self._proxy_username is not None:
            proxy["username"] = self._proxy_username
        if self._proxy_password is not None:
            proxy["password"] = self._proxy_password
        return proxy

    def _simulate_human_jitter(self, page: Any) -> None:
        for _ in range(2):
            self._sleep_human_delay()
            x = random.randint(50, self._viewport_width - 50)
            y = random.randint(50, self._viewport_height - 50)
            page.mouse.move(x, y)

    def _sleep_human_delay(self) -> None:
        delay_ms = random.randint(self._human_min_delay_ms, self._human_max_delay_ms)
        time.sleep(delay_ms / 1000)

    def _raise_if_bot_blocked(self, page: Any) -> None:
        page_text = page.content().lower()
        if any(marker in page_text for marker in self._challenge_markers):
            raise BotBlockedError("Bot challenge or blocking signal detected in page content.")

    def _stealth_init_script(self) -> str:
        return """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4] });
window.chrome = window.chrome || { runtime: {} };
"""

    def _target_domain(self) -> str:
        parsed = urlparse(self._portal_url)
        if parsed.hostname is None:
            return self._portal_url
        return parsed.hostname

    def _report_proxy_outcome(self, outcome: str) -> None:
        if (
            not self._proxy_v2_enabled
            or self._proxy_strategy is None
            or self._active_proxy_server is None
        ):
            return
        try:
            self._proxy_strategy.report_outcome(
                domain=self._target_domain(),
                proxy_server=self._active_proxy_server,
                outcome=outcome,
            )
        except Exception:
            if not self._proxy_strategy_failopen:
                raise
