"""Postgres loader unit tests."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
import pytest
from sqlalchemy.exc import SQLAlchemyError

from cofepris_brsdm_scraper.exceptions import DatabaseUnavailableError
from cofepris_brsdm_scraper.load.postgres_loader import PostgresLoader


@dataclass
class FakeConnection:
    """Minimal fake connection that records SQL statements."""

    statements: list[str] = field(default_factory=list)

    def execute(self, statement: object) -> None:
        self.statements.append(str(statement))


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


def test_postgres_loader_returns_rows_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    """Loader should return row metrics and execute swap statements."""
    dataframe = pd.DataFrame({"numero_de_registro": ["A"], "foo": ["bar"]})

    def fake_to_sql(self: pd.DataFrame, *args: object, **kwargs: object) -> None:  # noqa: ANN001
        return None

    monkeypatch.setattr(pd.DataFrame, "to_sql", fake_to_sql)

    engine = FakeEngine()
    loader = PostgresLoader(engine=engine, table_name="medicamentos", chunk_size=100)
    result = loader.load(dataframe)

    assert result.rows_loaded == 1
    assert result.table_name == "medicamentos"
    assert any("CREATE UNIQUE INDEX" in statement for statement in engine.connection.statements)


def test_postgres_loader_raises_database_unavailable_error() -> None:
    """Loader should wrap database errors into domain exception."""
    dataframe = pd.DataFrame({"numero_de_registro": ["A"]})
    loader = PostgresLoader(engine=FakeEngine(should_fail=True), table_name="medicamentos")
    with pytest.raises(DatabaseUnavailableError):
        loader.load(dataframe)
