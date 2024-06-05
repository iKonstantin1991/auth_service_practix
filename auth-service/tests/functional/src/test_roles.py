from http import HTTPStatus
from uuid import uuid4

import pytest

from tests.functional.conftest import Client
from tests.functional.plugins.users import TestUser
from tests.functional.plugins.roles import Role
from tests.functional.src.utils import build_headers, login


@pytest.mark.asyncio
async def test_get_roles_returns_roles_for_superuser(client: Client, superuser: TestUser) -> None:
    access_token, _ = await login(superuser, client)
    response = await client.get('api/v1/roles/', headers=build_headers(access_token))

    assert response.status == HTTPStatus.OK


@pytest.mark.asyncio
async def test_get_roles_returns_forbidden_for_regular_user(client: Client, user: TestUser) -> None:
    access_token, _ = await login(user, client)
    response = await client.get('api/v1/roles/', headers=build_headers(access_token))

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_get_roles_returns_unauthorized_if_no_token(client: Client) -> None:
    response = await client.get('api/v1/roles/')

    assert response.status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_role_returns_role_for_superuser(client: Client, superuser: TestUser) -> None:
    new_role_name = f'test role {uuid4()}'
    access_token, _ = await login(superuser, client)
    response = await client.post(
        'api/v1/roles/',
        body={'name': new_role_name},
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.CREATED
    body = await response.json()
    assert body['name'] == new_role_name


@pytest.mark.asyncio
async def test_create_role_returns_forbidden_if_role_exists(
    client: Client, superuser: TestUser, role: Role
) -> None:
    access_token, _ = await login(superuser, client)
    response = await client.post(
        'api/v1/roles/',
        body={'name': role.name},
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_create_role_returns_forbidden_for_regular_user(client: Client, user: TestUser) -> None:
    access_token, _ = await login(user, client)
    response = await client.post(
        'api/v1/roles/',
        body={'name': f'test role {uuid4()}'},
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_create_role_returns_unauthorized_if_no_token(client: Client) -> None:
    response = await client.post(
        'api/v1/roles/',
        body={'name': f'test role {uuid4()}'},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_role_successfully_deletes_role_for_superuser(
    client: Client, superuser: TestUser, role: Role
) -> None:
    access_token, _ = await login(superuser, client)
    response = await client.delete(
        f'api/v1/roles/{role.id}',
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_role_returns_forbidden_for_regular_user(client: Client, user: TestUser, role: Role) -> None:
    access_token, _ = await login(user, client)
    response = await client.delete(
        f'api/v1/roles/{role.id}',
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_delete_role_returns_unauthorized_if_no_token(client: Client, role: Role) -> None:
    response = await client.delete(
        f'api/v1/roles/{role.id}',
    )

    assert response.status == HTTPStatus.UNAUTHORIZED
