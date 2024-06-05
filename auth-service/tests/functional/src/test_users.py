from http import HTTPStatus
from uuid import uuid4

import pytest

from tests.functional.conftest import Client
from tests.functional.plugins.users import TestUser, TestUserWithRoles
from tests.functional.plugins.roles import TestRole
from tests.functional.src.utils import build_headers, login


@pytest.mark.asyncio
async def test_get_user_success(client: Client, user: TestUser) -> None:
    access_token, _ = await login(user, client, user_agent=f'test user agent {uuid4()}')

    response = await client.get(f'api/v1/users/{user.id}', headers=build_headers(access_token))

    assert response.status == HTTPStatus.OK
    body = await response.json()
    assert body['id'] == str(user.id)
    assert body['email'] == user.email


@pytest.mark.asyncio
async def test_get_user_without_permission(client: Client, user: TestUser) -> None:
    user_to_get = TestUser(id=uuid4(), email='user2@test.com', password='password')
    access_token, _ = await login(user, client, user_agent=f'test user agent {uuid4()}')

    response = await client.get(f'api/v1/users/{user_to_get.id}', headers=build_headers(access_token))

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_update_user_success(client: Client, user: TestUser) -> None:
    access_token, _ = await login(user, client, user_agent=f'test user agent {uuid4()}')
    email_to_update = 'new_email@test.com'
    password_to_update = 'new_password'

    response = await client.put(
        f'api/v1/users/{user.id}',
        body={'email': email_to_update, 'password': password_to_update},
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.OK
    body = await response.json()
    assert body['id'] == str(user.id)
    assert body['email'] == email_to_update


@pytest.mark.asyncio
async def test_update_user_without_permission(client: Client, user: TestUser) -> None:
    user_to_update = TestUser(id=uuid4(), email='user2@test.com', password='password')
    access_token, _ = await login(user, client, user_agent=f'test user agent {uuid4()}')
    email_to_update = 'new_email@test.com'
    password_to_update = 'new_password'

    response = await client.put(
        f'api/v1/users/{user_to_update.id}',
        body={'email': email_to_update, 'password': password_to_update},
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_assign_existing_role_to_another_by_superuser(
        client: Client,
        superuser: TestUser,
        user: TestUser,
        usual_user_role: TestRole
) -> None:
    access_token, _ = await login(superuser, client, user_agent=f'test user agent {uuid4()}')

    response = await client.post(
        f'api/v1/users/{user.id}/roles?role_id={usual_user_role.id}',
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.OK
    body = await response.json()
    assert body['id'] == str(usual_user_role.id)
    assert body['name'] == usual_user_role.name


@pytest.mark.asyncio
async def test_assign_existing_role_to_another_by_usual_user(
        client: Client,
        user: TestUser,
        usual_user_role: TestRole
) -> None:
    access_token, _ = await login(user, client, user_agent=f'test user agent {uuid4()}')
    user_to_assign_role = TestUser(id=uuid4(), email='user2@test.com', password='password')

    response = await client.post(
        f'api/v1/users/{user_to_assign_role.id}/roles?role_id={usual_user_role.id}',
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_assign_not_existing_role(client: Client, superuser: TestUser) -> None:
    access_token, _ = await login(superuser, client, user_agent=f'test user agent {uuid4()}')

    response = await client.post(
        f'api/v1/users/{superuser.id}/roles?role_id={uuid4()}',
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_dissociate_existing_role_to_another_by_superuser(
        client: Client,
        superuser: TestUser,
        user: TestUser,
        usual_user_role: TestRole
) -> None:
    access_token, _ = await login(superuser, client, user_agent=f'test user agent {uuid4()}')

    response = await client.delete(
        f'api/v1/users/{user.id}/roles?role_id={usual_user_role.id}',
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_dissociate_existing_role_to_another_by_usual_user(
        client: Client,
        user: TestUser,
        usual_user_role: TestRole
) -> None:
    access_token, _ = await login(user, client, user_agent=f'test user agent {uuid4()}')
    user_to_dissociate_role = TestUser(id=uuid4(), email='user2@test.com', password='password')

    response = await client.post(
        f'api/v1/users/{user_to_dissociate_role.id}/roles?role_id={usual_user_role.id}',
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_dissociate_not_existing_role(client: Client, superuser: TestUser) -> None:
    access_token, _ = await login(superuser, client, user_agent=f'test user agent {uuid4()}')

    response = await client.post(
        f'api/v1/users/{superuser.id}/roles?role_id={uuid4()}',
        headers=build_headers(access_token)
    )

    assert response.status == HTTPStatus.NOT_FOUND
