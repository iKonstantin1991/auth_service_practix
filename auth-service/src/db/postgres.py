from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from core.config import settings

Base = declarative_base()
dsn = (f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@'
       f'{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}')
engine = create_async_engine(dsn, echo=settings.echo_in_db, future=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
