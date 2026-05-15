"""Scheduler daemon implementation."""

from __future__ import annotations

import structlog
from apscheduler.schedulers.blocking import BlockingScheduler
from filelock import FileLock, Timeout

from cofepris_brsdm_scraper.pipeline.orchestrator import Orchestrator


class PipelineDaemon:
    """Run pipeline periodically using cron expressions."""

    def __init__(self, orchestrator: Orchestrator, cron_expression: str, lock_path: str) -> None:
        self._orchestrator = orchestrator
        self._cron_expression = cron_expression
        self._lock_path = lock_path
        self._logger = structlog.get_logger(__name__)

    def run_forever(self) -> None:
        """Start blocking scheduler with configured cron trigger."""
        scheduler = BlockingScheduler()
        minute, hour, day, month, day_of_week = self._cron_expression.split(" ")
        scheduler.add_job(
            self._run_job,
            trigger="cron",
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            id="cofepris-pipeline-job",
            replace_existing=True,
        )
        scheduler.start()

    def _run_job(self) -> None:
        lock = FileLock(self._lock_path, timeout=0)
        try:
            with lock:
                report = self._orchestrator.run()
                self._logger.info(
                    "pipeline_run_finished",
                    rows_loaded=report.rows_loaded,
                    scraper_ms=report.scraper_ms,
                    transform_ms=report.transform_ms,
                    load_ms=report.load_ms,
                )
        except Timeout:
            self._logger.warning("pipeline_run_skipped", skipped=True, reason="already_running")
