from typing import Awaitable
from http import HTTPStatus
from unittest.mock import Mock

from aiohttp import ClientResponse
import pytest


@pytest.mark.asyncio
async def test_login_returns_tokens(make_post_request: Awaitable[ClientResponse], user: Mock) -> None:
    response = await make_post_request(
        'api/v1/auth/login',
        body={'email': user.email, 'password': user.password},
    )
    assert response.status == HTTPStatus.OK
    body = await response.json()
    assert 'access_token' in body
    assert 'refresh_token' in body


@pytest.mark.asyncio
async def test_get_auth_history_returns_unauthorized_if_no_token(make_get_request: Awaitable[ClientResponse]) -> None:
    response = await make_get_request('api/v1/auth/history')
    assert response.status == HTTPStatus.UNAUTHORIZED
