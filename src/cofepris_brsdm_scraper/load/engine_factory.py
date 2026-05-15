"""SQLAlchemy engine factory."""

from sqlalchemy import Engine, create_engine


class EngineFactory:
    """Create SQLAlchemy engines from connection URLs."""

    @staticmethod
    def create(database_url: str) -> Engine:
        return create_engine(database_url, future=True)
