from typing import Iterator

import pytest_asyncio
from redis.asyncio import Redis

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope='session')
async def redis_client() -> Iterator[Redis]:
    redis_client = Redis(
        host=test_settings.redis_host, port=test_settings.redis_port
    )
    yield redis_client
    await redis_client.aclose()


@pytest_asyncio.fixture
async def redis_flushall(redis_client: Redis) -> Iterator[None]:
    yield
    await redis_client.flushall()
