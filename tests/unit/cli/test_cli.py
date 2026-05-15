"""CLI tests."""

from __future__ import annotations

from dataclasses import dataclass

from typer.testing import CliRunner

from cofepris_brsdm_scraper.cli.main import app
from cofepris_brsdm_scraper.exceptions import DownloadError


@dataclass
class FakeReport:
    rows_loaded: int = 10
    table_name: str = "medicamentos"
    scraper_ms: int = 1
    transform_ms: int = 1
    load_ms: int = 1


class FakeOrchestrator:
    def run(self) -> FakeReport:
        return FakeReport()


class FailingDownloadOrchestrator:
    def run(self) -> FakeReport:
        raise DownloadError("Portal timed out")


def test_cli_run_returns_success_json(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """CLI run command should return successful output."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setattr(
        "cofepris_brsdm_scraper.cli.main._build_orchestrator",
        lambda _settings: FakeOrchestrator(),
    )

    runner = CliRunner()
    result = runner.invoke(app, ["run"])
    assert result.exit_code == 0
    assert '"status": "ok"' in result.output


def test_cli_run_prints_download_error_before_exit(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """CLI run command should print actionable context on download failures."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setattr(
        "cofepris_brsdm_scraper.cli.main._build_orchestrator",
        lambda _settings: FailingDownloadOrchestrator(),
    )

    runner = CliRunner()
    result = runner.invoke(app, ["run"])
    assert result.exit_code == 10
    assert "Portal timed out" in result.output
