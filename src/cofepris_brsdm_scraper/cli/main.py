"""CLI entrypoint for the BRSDM pipeline."""

from __future__ import annotations

import json

import typer

from cofepris_brsdm_scraper.config.settings import Settings
from cofepris_brsdm_scraper.exceptions import (
    DatabaseUnavailableError,
    DownloadError,
    MissingColumnError,
    PipelineError,
    PortalUIChangedError,
)
from cofepris_brsdm_scraper.load.engine_factory import EngineFactory
from cofepris_brsdm_scraper.load.postgres_loader import PostgresLoader
from cofepris_brsdm_scraper.load.scraping_attempt_logger import ScrapingAttemptLogger
from cofepris_brsdm_scraper.logging_setup.config import configure_logging
from cofepris_brsdm_scraper.pipeline.orchestrator import Orchestrator
from cofepris_brsdm_scraper.scheduling.daemon import PipelineDaemon
from cofepris_brsdm_scraper.scraper.downloader import Downloader
from cofepris_brsdm_scraper.scraper.proxy_strategy import ProxyStrategy
from cofepris_brsdm_scraper.transform.normalizer import Normalizer

app = typer.Typer(add_completion=False)


def _exit_with_error_message(exc: Exception, code: int) -> None:
    message = str(exc) or exc.__class__.__name__
    typer.echo(message, err=True)
    raise typer.Exit(code=code) from exc


def _build_orchestrator(settings: Settings) -> Orchestrator:
    engine = EngineFactory.create(settings.database_url)
    proxy_strategy = None
    if settings.scraper_proxy_v2_enabled and settings.scraper_proxy_servers:
        proxy_strategy = ProxyStrategy(
            engine=engine,
            proxy_servers=settings.scraper_proxy_servers,
            proxy_username=settings.scraper_proxy_username,
            proxy_password=settings.scraper_proxy_password,
            circuit_failure_threshold=settings.scraper_proxy_circuit_failure_threshold,
            circuit_cooldown_seconds=settings.scraper_proxy_circuit_cooldown_seconds,
            half_open_max_trials=settings.scraper_proxy_half_open_max_trials,
            sticky_ttl_seconds=settings.scraper_proxy_sticky_ttl_seconds,
            health_decay_on_success=settings.scraper_proxy_health_decay_on_success,
            health_penalty_timeout=settings.scraper_proxy_health_penalty_timeout,
            health_penalty_block=settings.scraper_proxy_health_penalty_block,
            fail_open=settings.scraper_proxy_strategy_failopen,
        )
    downloader = Downloader(
        portal_url=settings.portal_url,
        retries=settings.scraper_retries,
        timeout_ms=settings.scraper_timeout_ms,
        backoff_seconds=settings.scraper_backoff_seconds,
        stealth_enabled=settings.scraper_stealth_enabled,
        headless=settings.scraper_headless,
        user_agent=settings.scraper_user_agent,
        viewport_width=settings.scraper_viewport_width,
        viewport_height=settings.scraper_viewport_height,
        locale=settings.scraper_locale,
        timezone_id=settings.scraper_timezone_id,
        proxy_servers=settings.scraper_proxy_servers,
        proxy_username=settings.scraper_proxy_username,
        proxy_password=settings.scraper_proxy_password,
        proxy_strategy=proxy_strategy,
        proxy_v2_enabled=settings.scraper_proxy_v2_enabled,
        proxy_strategy_failopen=settings.scraper_proxy_strategy_failopen,
    )
    normalizer = Normalizer()
    loader = PostgresLoader(
        engine=engine,
        table_name=settings.table_name,
        chunk_size=settings.load_chunk_size,
    )
    attempt_logger = ScrapingAttemptLogger(
        engine=engine,
        table_name=settings.attempts_table_name,
    )
    return Orchestrator(
        downloader=downloader,
        normalizer=normalizer,
        loader=loader,
        attempt_logger=attempt_logger,
    )


@app.command("run")
def run_pipeline() -> None:
    """Execute one pipeline run."""
    settings = Settings()
    configure_logging(settings.log_level)
    orchestrator = _build_orchestrator(settings)
    try:
        report = orchestrator.run()
        typer.echo(
            json.dumps(
                {
                    "status": "ok",
                    "rows_loaded": report.rows_loaded,
                    "table_name": report.table_name,
                    "scraper_ms": report.scraper_ms,
                    "transform_ms": report.transform_ms,
                    "load_ms": report.load_ms,
                }
            )
        )
    except (DownloadError, PortalUIChangedError) as exc:
        _exit_with_error_message(exc=exc, code=10)
    except MissingColumnError as exc:
        _exit_with_error_message(exc=exc, code=20)
    except DatabaseUnavailableError as exc:
        _exit_with_error_message(exc=exc, code=30)
    except PipelineError as exc:
        _exit_with_error_message(exc=exc, code=40)


@app.command("daemon")
def daemon(
    cron: str | None = typer.Option(default=None, help="Cron expression with 5 fields"),
) -> None:
    """Run scheduler daemon mode."""
    settings = Settings()
    configure_logging(settings.log_level)
    orchestrator = _build_orchestrator(settings)
    daemon_runner = PipelineDaemon(
        orchestrator=orchestrator,
        cron_expression=cron or settings.cron_expression,
        lock_path=settings.lock_path,
    )
    daemon_runner.run_forever()
