from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from core.config import settings

Base = declarative_base()
dsn = (f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@'
       f'{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}')
engine = create_async_engine(dsn, echo=True, future=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
