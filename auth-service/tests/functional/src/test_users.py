from http import HTTPStatus
from uuid import uuid4

import pytest

from tests.functional.conftest import Client
from tests.functional.plugins.users import TestUser
from tests.functional.plugins.roles import Role
from tests.functional.src.utils import build_headers, login


@pytest.mark.asyncio
async def test_get_user_success(client: Client, user: TestUser) -> None:
    access_token, _ = await login(user, client)

    response = await client.get(
        f'api/v1/users/{user.id}', headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.OK
    body = await response.json()
    assert body['id'] == str(user.id)
    assert body['email'] == user.email


@pytest.mark.asyncio
async def test_get_user_without_permission(
    client: Client, user: TestUser, superuser: TestUser
) -> None:
    access_token, _ = await login(user, client)

    response = await client.get(
        f'api/v1/users/{superuser.id}', headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_update_user_success(client: Client, user: TestUser) -> None:
    access_token, _ = await login(user, client)
    email_to_update = 'new_email@test.com'
    password_to_update = 'new_password'

    response = await client.put(
        f'api/v1/users/{user.id}',
        body={'email': email_to_update, 'password': password_to_update},
        headers=build_headers(access_token),
    )

    assert response.status == HTTPStatus.OK
    body = await response.json()
    assert body['id'] == str(user.id)
    assert body['email'] == email_to_update


@pytest.mark.asyncio
async def test_update_user_without_permission(
    client: Client, user: TestUser, superuser: TestUser
) -> None:
    access_token, _ = await login(user, client)
    email_to_update = 'new_email@test.com'
    password_to_update = 'new_password'

    response = await client.put(
        f'api/v1/users/{superuser.id}',
        body={'email': email_to_update, 'password': password_to_update},
        headers=build_headers(access_token),
    )

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_get_user_roles_returns_roles_superuser(
    client: Client, superuser: TestUser, user: TestUser
) -> None:
    access_token, _ = await login(superuser, client)

    response = await client.get(
        f'api/v1/users/{user.id}/roles', headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.OK
    body = await response.json()
    assert len(body) == len(user.roles)
    assert body[0]['id'] == str(user.roles[0].id)
    assert body[0]['name'] == user.roles[0].name


@pytest.mark.asyncio
async def test_get_user_roles_returns_forbidden_regular_user(
    client: Client, user: TestUser, superuser: TestUser
) -> None:
    access_token, _ = await login(user, client)

    response = await client.get(
        f'api/v1/users/{superuser.id}/roles',
        headers=build_headers(access_token),
    )

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_assign_existing_role_to_another_by_superuser(
    client: Client, superuser: TestUser, user: TestUser, role: Role
) -> None:
    access_token, _ = await login(superuser, client)

    response = await client.post(
        f'api/v1/users/{user.id}/roles?role_id={role.id}',
        headers=build_headers(access_token),
    )

    assert response.status == HTTPStatus.OK
    body = await response.json()
    assert body['id'] == str(role.id)
    assert body['name'] == role.name


@pytest.mark.asyncio
async def test_assign_existing_role_to_another_by_regular_user(
    client: Client, superuser: TestUser, user: TestUser, role: Role
) -> None:
    access_token, _ = await login(user, client)

    response = await client.post(
        f'api/v1/users/{superuser.id}/roles?role_id={role.id}',
        headers=build_headers(access_token),
    )

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_assign_not_existing_role(
    client: Client, superuser: TestUser
) -> None:
    access_token, _ = await login(superuser, client)

    response = await client.post(
        f'api/v1/users/{superuser.id}/roles?role_id={uuid4()}',
        headers=build_headers(access_token),
    )

    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_dissociate_existing_role_to_another_by_superuser(
    client: Client,
    superuser: TestUser,
    user: TestUser,
) -> None:
    access_token, _ = await login(superuser, client)

    response = await client.delete(
        f'api/v1/users/{user.id}/roles?role_id={user.roles[0].id}',
        headers=build_headers(access_token),
    )

    assert response.status == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_dissociate_existing_role_to_another_by_usual_user(
    client: Client, user: TestUser, superuser: TestUser
) -> None:
    access_token, _ = await login(user, client)

    response = await client.post(
        f'api/v1/users/{superuser.id}/roles?role_id={superuser.roles[0].id}',
        headers=build_headers(access_token),
    )

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_dissociate_not_existing_role(
    client: Client, superuser: TestUser
) -> None:
    access_token, _ = await login(superuser, client)

    response = await client.post(
        f'api/v1/users/{superuser.id}/roles?role_id={uuid4()}',
        headers=build_headers(access_token),
    )

    assert response.status == HTTPStatus.NOT_FOUND
