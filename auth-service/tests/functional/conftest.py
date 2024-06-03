from typing import Dict
import asyncio

import aiohttp
import pytest_asyncio

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def aiohttp_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
async def make_get_request(aiohttp_session):
    async def inner(path: str, params: Dict[str, str] | None = None):
        url = f'http://{test_settings.service_host}:{test_settings.service_port}/{path}'
        return await aiohttp_session.get(url, params=(params or {}))
    return inner


@pytest_asyncio.fixture
async def make_post_request(aiohttp_session):
    async def inner(path: str, body: Dict[str, str] | None = None):
        url = f'http://{test_settings.service_host}:{test_settings.service_port}/{path}'
        return await aiohttp_session.post(url, json=(body or {}))
    return inner


@pytest_asyncio.fixture(scope="session")
def db_tables():
    # create all required tables
    # drop all tables after test
    pass


@pytest_asyncio.fixture
def fixture_user(db_tables):
    # user without roles
    # have to hash password
    pass


@pytest_asyncio.fixture
def fixture_superuser(db_tables):
    # user with superuser role, so we have to create and assign role as well
    # have to hash password
    pass
