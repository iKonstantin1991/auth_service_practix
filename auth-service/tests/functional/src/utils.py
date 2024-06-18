from http import HTTPStatus
from typing import Dict, Tuple

from unittest.mock import Mock
from tests.functional.conftest import Client


async def login(
    user: Mock, client: Client, user_agent: str = 'user agent'
) -> Tuple[str, str]:
    response = await client.post(
        'api/v1/auth/login',
        body={'email': user.email, 'password': user.password},
        headers=build_headers(user_agent=user_agent),
    )
    assert response.status == HTTPStatus.OK
    body = await response.json()
    return body['access_token'], body['refresh_token']


def build_headers(
    token: str | None = None, user_agent: str = 'user agent'
) -> Dict[str, str]:
    headers = {'User-Agent': user_agent}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers
