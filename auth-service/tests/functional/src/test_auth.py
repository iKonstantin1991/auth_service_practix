from http import HTTPStatus
from uuid import uuid4

import pytest

from tests.functional.conftest import Client
from tests.functional.plugins.users import TestUser
from tests.functional.src.utils import build_headers, login


@pytest.mark.asyncio
async def test_login_returns_tokens(client: Client, user: TestUser) -> None:
    response = await client.post(
        'api/v1/auth/login',
        body={'email': user.email, 'password': user.password},
    )

    assert response.status == HTTPStatus.OK
    body = await response.json()
    assert 'access_token' in body
    assert 'refresh_token' in body


@pytest.mark.asyncio
async def test_get_auth_history_returns_history(client: Client, user: TestUser) -> None:
    user_agent = f'test user agent {uuid4()}'

    access_token, _ = await login(user, client, user_agent)
    response = await client.get('api/v1/auth/history', headers=build_headers(access_token))

    assert response.status == HTTPStatus.OK
    body = await response.json()
    assert len(body) == 1
    assert body[0]['user_agent'] == user_agent


@pytest.mark.asyncio
async def test_get_auth_history_returns_unauthorized_if_no_token(client: Client) -> None:
    response = await client.get('api/v1/auth/history')

    assert response.status == HTTPStatus.UNAUTHORIZED
