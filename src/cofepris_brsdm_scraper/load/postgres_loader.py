"""PostgreSQL load implementation."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from cofepris_brsdm_scraper.exceptions import DatabaseUnavailableError


@dataclass(frozen=True)
class LoadResult:
    """Result metrics for a successful load."""

    rows_loaded: int
    table_name: str


class PostgresLoader:
    """Load normalized DataFrame into PostgreSQL using replace strategy."""

    def __init__(self, engine: Engine, table_name: str, chunk_size: int = 10000) -> None:
        self._engine = engine
        self._table_name = table_name
        self._chunk_size = chunk_size

    def load(self, dataframe: pd.DataFrame) -> LoadResult:
        """Replace target table content with given DataFrame atomically."""
        staging_table = f"{self._table_name}__staging"
        backup_table = f"{self._table_name}__backup"
        try:
            with self._engine.begin() as connection:
                dataframe.to_sql(
                    staging_table,
                    con=connection,
                    if_exists="replace",
                    index=False,
                    chunksize=self._chunk_size,
                )

                connection.execute(text(f'DROP TABLE IF EXISTS "{backup_table}"'))
                connection.execute(
                    text(
                        f'ALTER TABLE IF EXISTS "{self._table_name}" '
                        f'RENAME TO "{backup_table}"'
                    )
                )
                connection.execute(
                    text(f'ALTER TABLE "{staging_table}" RENAME TO "{self._table_name}"')
                )
                connection.execute(
                    text(
                        f"CREATE UNIQUE INDEX IF NOT EXISTS "
                        f'"{self._table_name}_numero_de_registro_uidx" '
                        f'ON "{self._table_name}" ("numero_de_registro")'
                    )
                )
                connection.execute(text(f'DROP TABLE IF EXISTS "{backup_table}"'))
        except SQLAlchemyError as exc:
            raise DatabaseUnavailableError(
                "Database load failed during transactional replace."
            ) from exc

        return LoadResult(rows_loaded=len(dataframe.index), table_name=self._table_name)
