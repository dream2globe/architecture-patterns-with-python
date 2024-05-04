import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from src.orm import mapper_registry, start_mappers


@pytest.fixture(scope="session")
def in_memory_db():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
    mapper_registry.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="session")
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()
