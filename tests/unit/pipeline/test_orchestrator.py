"""Orchestrator unit tests."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from cofepris_brsdm_scraper.load.postgres_loader import LoadResult
from cofepris_brsdm_scraper.pipeline.orchestrator import Orchestrator


class FakeDownloader:
    """Downloader fake that creates a temporary file."""

    def download(self, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "download.xlsx"
        path.write_text("mock", encoding="utf-8")
        return path


class FakeNormalizer:
    """Normalizer fake returning one-row DataFrame."""

    def normalize(self, excel_path: Path) -> pd.DataFrame:
        return pd.DataFrame({"numero_de_registro": ["A"]})


class FakeLoader:
    """Loader fake returning one loaded row."""

    def load(self, dataframe: pd.DataFrame) -> LoadResult:
        return LoadResult(rows_loaded=len(dataframe.index), table_name="medicamentos")


class FakeFailingLoader:
    """Loader fake that raises a runtime error."""

    def load(self, dataframe: pd.DataFrame) -> LoadResult:
        raise RuntimeError("load failed")


class FakeAttemptLogger:
    """Recorder fake for scraping attempts."""

    def __init__(self) -> None:
        self.calls: list[tuple[datetime, bool, str | None]] = []

    def log_attempt(
        self,
        attempted_at: datetime,
        was_successful: bool,
        failure_cause: str | None = None,
    ) -> None:
        self.calls.append((attempted_at, was_successful, failure_cause))


def test_orchestrator_runs_all_stages_and_returns_report(tmp_path: Path) -> None:
    """Orchestrator should execute stages in order and return metrics."""
    attempt_logger = FakeAttemptLogger()
    orchestrator = Orchestrator(
        downloader=FakeDownloader(),
        normalizer=FakeNormalizer(),
        loader=FakeLoader(),
        attempt_logger=attempt_logger,
        temp_dir=tmp_path / "tmp",
    )
    report = orchestrator.run()

    assert report.rows_loaded == 1
    assert report.table_name == "medicamentos"
    assert report.scraper_ms >= 0
    assert report.transform_ms >= 0
    assert report.load_ms >= 0
    assert not (tmp_path / "tmp" / "download.xlsx").exists()
    assert len(attempt_logger.calls) == 1
    assert attempt_logger.calls[0][1:] == (True, None)


def test_orchestrator_logs_failure_with_error_cause(tmp_path: Path) -> None:
    """Orchestrator should persist failed attempts with the exception cause."""
    attempt_logger = FakeAttemptLogger()
    orchestrator = Orchestrator(
        downloader=FakeDownloader(),
        normalizer=FakeNormalizer(),
        loader=FakeFailingLoader(),
        attempt_logger=attempt_logger,
        temp_dir=tmp_path / "tmp",
    )

    with pytest.raises(RuntimeError, match="load failed"):
        orchestrator.run()

    assert len(attempt_logger.calls) == 1
    assert attempt_logger.calls[0][1:] == (False, "load failed")
    assert not (tmp_path / "tmp" / "download.xlsx").exists()
