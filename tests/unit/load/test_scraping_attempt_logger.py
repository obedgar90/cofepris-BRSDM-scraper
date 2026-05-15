"""Scraping attempt logger unit tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import SQLAlchemyError

from cofepris_brsdm_scraper.exceptions import DatabaseUnavailableError
from cofepris_brsdm_scraper.load.scraping_attempt_logger import ScrapingAttemptLogger


@dataclass
class FakeConnection:
    """Minimal fake connection that records SQL statements and params."""

    statements: list[tuple[str, dict[str, object]]] = field(default_factory=list)

    def execute(self, statement: object, params: dict[str, object] | None = None) -> None:
        self.statements.append((str(statement), params or {}))


class FakeBeginContext:
    """Context manager returned by fake engine begin()."""

    def __init__(self, connection: FakeConnection) -> None:
        self._connection = connection

    def __enter__(self) -> FakeConnection:
        return self._connection

    def __exit__(self, *_args: object) -> None:
        return None


class FakeEngine:
    """Fake SQLAlchemy engine."""

    def __init__(self, should_fail: bool = False) -> None:
        self.connection = FakeConnection()
        self.should_fail = should_fail

    def begin(self) -> FakeBeginContext:
        if self.should_fail:
            raise SQLAlchemyError("db down")
        return FakeBeginContext(self.connection)


def test_logger_inserts_successful_attempt() -> None:
    """Logger should store successful attempts without failure cause."""
    engine = FakeEngine()
    logger = ScrapingAttemptLogger(engine=engine)
    attempted_at = datetime(2026, 5, 13, 22, 27, tzinfo=UTC)

    logger.log_attempt(attempted_at=attempted_at, was_successful=True)

    assert len(engine.connection.statements) == 2
    insert_params = engine.connection.statements[1][1]
    assert insert_params["attempted_at"] == attempted_at
    assert insert_params["was_successful"] is True
    assert insert_params["failure_cause"] is None


def test_logger_inserts_failed_attempt_with_cause() -> None:
    """Logger should persist failure cause when attempt fails."""
    engine = FakeEngine()
    logger = ScrapingAttemptLogger(engine=engine)
    attempted_at = datetime(2026, 5, 13, 22, 27, tzinfo=UTC)

    logger.log_attempt(
        attempted_at=attempted_at,
        was_successful=False,
        failure_cause="portal timeout",
    )

    insert_params = engine.connection.statements[1][1]
    assert insert_params["attempted_at"] == attempted_at
    assert insert_params["was_successful"] is False
    assert insert_params["failure_cause"] == "portal timeout"


def test_logger_wraps_database_errors() -> None:
    """Logger should convert SQL errors into domain exception."""
    logger = ScrapingAttemptLogger(engine=FakeEngine(should_fail=True))

    with pytest.raises(DatabaseUnavailableError):
        logger.log_attempt(attempted_at=datetime.now(tz=UTC), was_successful=True)
