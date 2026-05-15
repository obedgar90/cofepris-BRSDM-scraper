"""Persistence for scraping attempt audit records."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from cofepris_brsdm_scraper.exceptions import DatabaseUnavailableError


class ScrapingAttemptLogger:
    """Store scraping attempt outcomes in a PostgreSQL table."""

    def __init__(self, engine: Engine, table_name: str = "scraping_attempts") -> None:
        self._engine = engine
        self._table_name = table_name

    def log_attempt(
        self,
        attempted_at: datetime,
        was_successful: bool,
        failure_cause: str | None = None,
    ) -> None:
        """Insert one attempt row with timestamp, outcome and optional cause."""
        create_sql = text(
            f"""
            CREATE TABLE IF NOT EXISTS "{self._table_name}" (
                id BIGSERIAL PRIMARY KEY,
                attempted_at TIMESTAMPTZ NOT NULL,
                was_successful BOOLEAN NOT NULL,
                failure_cause TEXT NULL
            )
            """
        )
        insert_sql = text(
            f"""
            INSERT INTO "{self._table_name}" (attempted_at, was_successful, failure_cause)
            VALUES (:attempted_at, :was_successful, :failure_cause)
            """
        )
        try:
            with self._engine.begin() as connection:
                connection.execute(create_sql)
                connection.execute(
                    insert_sql,
                    {
                        "attempted_at": attempted_at,
                        "was_successful": was_successful,
                        "failure_cause": failure_cause,
                    },
                )
        except SQLAlchemyError as exc:
            raise DatabaseUnavailableError("Failed to persist scraping attempt audit record.") from exc
