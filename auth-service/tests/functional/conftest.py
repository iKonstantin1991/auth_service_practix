from typing import Awaitable, Dict, Iterator
import asyncio

from aiohttp import ClientSession, ClientResponse
import pytest_asyncio

from tests.functional.settings import test_settings

pytest_plugins = [
    'tests.functional.plugins.db',
    'tests.functional.plugins.users',
    'tests.functional.plugins.roles',
    'tests.functional.plugins.redis',
    'tests.functional.plugins.roles',
]

_BASE_URL = f'http://{test_settings.service_host}:{test_settings.service_port}'


class Client:
    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def get(
        self,
        path: str,
        params: Dict[str, str] | None = None,
        headers: Dict[str, str] | None = None,
    ) -> ClientResponse:
        return await self._session.get(
            f'{_BASE_URL}/{path}',
            params=(params or {}),
            headers=(headers or {}),
        )

    async def post(
        self,
        path: str,
        body: Dict[str, str] | None = None,
        headers: Dict[str, str] | None = None,
    ) -> ClientResponse:
        return await self._session.post(
            f'{_BASE_URL}/{path}', json=(body or {}), headers=(headers or {})
        )

    async def put(
        self,
        path: str,
        body: Dict[str, str] | None = None,
        headers: Dict[str, str] | None = None,
    ) -> ClientResponse:
        return await self._session.put(
            f'{_BASE_URL}/{path}', json=(body or {}), headers=(headers or {})
        )

    async def delete(
        self, path: str, headers: Dict[str, str] | None = None
    ) -> ClientResponse:
        return await self._session.delete(
            f'{_BASE_URL}/{path}', headers=(headers or {})
        )


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
async def client(aiohttp_session: ClientSession) -> Awaitable[ClientResponse]:
    return Client(aiohttp_session)
