from typing import Awaitable, Dict, Iterator
import asyncio

from aiohttp import ClientSession, ClientResponse
import pytest_asyncio

from tests.functional.settings import test_settings

pytest_plugins = ['tests.functional.plugins.db', 'tests.functional.plugins.users']

_BASE_URL = f'http://{test_settings.service_host}:{test_settings.service_port}'


@pytest_asyncio.fixture(scope='session')
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session', name='aiohttp_session')
async def fixture_aiohttp_session() -> Iterator[ClientSession]:
    session = ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
async def make_get_request(aiohttp_session: ClientSession) -> Awaitable[ClientResponse]:
    async def inner(path: str, params: Dict[str, str] | None = None) -> ClientResponse:
        return await aiohttp_session.get(f'{_BASE_URL}/{path}', params=(params or {}))
    return inner


@pytest_asyncio.fixture
async def make_post_request(aiohttp_session: ClientSession) -> Awaitable[ClientResponse]:
    async def inner(path: str, body: Dict[str, str] | None = None) -> ClientResponse:
        return await aiohttp_session.post(f'{_BASE_URL}/{path}', json=(body or {}))
    return inner
