from typing import Iterator

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import pytest_asyncio

from tests.functional.settings import test_settings
from tests.functional.plugins.models import Base


dsn = (f'postgresql+asyncpg://{test_settings.postgres_user}:{test_settings.postgres_password}@'
       f'{test_settings.postgres_host}:{test_settings.postgres_port}/{test_settings.postgres_db}')
engine = create_async_engine(dsn, future=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope='session')
async def db_session() -> Iterator[AsyncSession]:
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_tables() -> Iterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
