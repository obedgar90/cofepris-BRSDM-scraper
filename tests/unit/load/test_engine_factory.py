"""Engine factory tests."""

from sqlalchemy.engine import Engine

from cofepris_brsdm_scraper.load.engine_factory import EngineFactory


def test_engine_factory_creates_engine_from_database_url() -> None:
    """EngineFactory must build SQLAlchemy engine."""
    engine = EngineFactory.create("sqlite+pysqlite:///:memory:")
    assert isinstance(engine, Engine)
