"""Pipeline orchestration use case."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

import pandas as pd

from cofepris_brsdm_scraper.load.postgres_loader import LoadResult


class DownloaderPort(Protocol):
    """Download behavior contract."""

    def download(self, output_dir: Path) -> Path: ...


class NormalizerPort(Protocol):
    """Normalization behavior contract."""

    def normalize(self, excel_path: Path) -> pd.DataFrame: ...


class LoaderPort(Protocol):
    """Load behavior contract."""

    def load(self, dataframe: pd.DataFrame) -> LoadResult: ...


class AttemptLoggerPort(Protocol):
    """Scraping attempt persistence contract."""

    def log_attempt(
        self,
        attempted_at: datetime,
        was_successful: bool,
        failure_cause: str | None = None,
    ) -> None: ...


@dataclass(frozen=True)
class RunReport:
    """Pipeline run metrics."""

    rows_loaded: int
    scraper_ms: int
    transform_ms: int
    load_ms: int
    table_name: str


class Orchestrator:
    """Coordinate scraper -> transform -> load stages."""

    def __init__(
        self,
        downloader: DownloaderPort,
        normalizer: NormalizerPort,
        loader: LoaderPort,
        attempt_logger: AttemptLoggerPort | None = None,
        temp_dir: Path = Path("tmp/cofepris"),
    ) -> None:
        self._downloader = downloader
        self._normalizer = normalizer
        self._loader = loader
        self._attempt_logger = attempt_logger
        self._temp_dir = temp_dir

    def run(self) -> RunReport:
        """Execute all stages and return metrics."""
        attempted_at = datetime.now(tz=UTC)
        downloaded_file: Path | None = None
        try:
            scraper_start = time.perf_counter()
            downloaded_file = self._downloader.download(self._temp_dir)
            scraper_ms = int((time.perf_counter() - scraper_start) * 1000)

            transform_start = time.perf_counter()
            dataframe = self._normalizer.normalize(downloaded_file)
            transform_ms = int((time.perf_counter() - transform_start) * 1000)

            load_start = time.perf_counter()
            load_result = self._loader.load(dataframe)
            load_ms = int((time.perf_counter() - load_start) * 1000)

            report = RunReport(
                rows_loaded=load_result.rows_loaded,
                scraper_ms=scraper_ms,
                transform_ms=transform_ms,
                load_ms=load_ms,
                table_name=load_result.table_name,
            )
            self._log_attempt(attempted_at=attempted_at, was_successful=True)
            return report
        except Exception as exc:
            failure_cause = str(exc) or exc.__class__.__name__
            try:
                self._log_attempt(
                    attempted_at=attempted_at,
                    was_successful=False,
                    failure_cause=failure_cause,
                )
            except Exception as logging_exc:
                exc.add_note(f"Also failed to persist attempt audit record: {logging_exc}")
            raise
        finally:
            if downloaded_file and downloaded_file.exists():
                downloaded_file.unlink()

    def _log_attempt(
        self,
        attempted_at: datetime,
        was_successful: bool,
        failure_cause: str | None = None,
    ) -> None:
        if self._attempt_logger is None:
            return
        self._attempt_logger.log_attempt(
            attempted_at=attempted_at,
            was_successful=was_successful,
            failure_cause=failure_cause,
        )
