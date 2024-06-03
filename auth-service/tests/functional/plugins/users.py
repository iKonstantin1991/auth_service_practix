from uuid import uuid4
import hashlib
from unittest.mock import Mock

import pytest_asyncio

from tests.functional.plugins.models import User, Role


@pytest_asyncio.fixture(name='user')
async def fixture_user(db_session):
    email = f'{uuid4()}@test.com'
    password = 'password'
    user = User(
        id=uuid4(),
        email=email,
        hashed_password=_hash_password(email, password),
    )
    db_session.add(user)
    await db_session.commit()
    yield Mock(email=user.email, password=password)


@pytest_asyncio.fixture(name='superuser')
async def fixture_superuser(db_session, superuser_role):
    email = f'{uuid4()}@test.com'
    password = 'password'
    user = User(
        id=uuid4(),
        email=email,
        hashed_password=_hash_password(email, password),
        roles=[superuser_role],
    )
    db_session.add(user)
    await db_session.commit()
    yield Mock(email=user.email, password=password)


@pytest_asyncio.fixture(scope='session', name='superuser_role')
async def fixture_superuser_role(db_session):
    superuser_role = Role(id=uuid4(), name='superuser')
    db_session.add(role)
    await db_session.commit()
    yield superuser_role


def _hash_password(salt: str, password: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
