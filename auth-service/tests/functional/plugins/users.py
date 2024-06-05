from typing import Iterator
from uuid import uuid4, UUID
import hashlib

import pytest_asyncio
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from tests.functional.plugins.models import User, Role


class TestUser(BaseModel):
    __test__ = False

    email: str
    password: str


@pytest_asyncio.fixture(name='user')
async def fixture_user(db_session: AsyncSession) -> Iterator[TestUser]:
    email = f'{uuid4()}@test.com'
    password = 'password'
    user = User(
        id=uuid4(),
        email=email,
        hashed_password=_hash_password(email, password),
    )
    db_session.add(user)
    await db_session.commit()
    yield TestUser(email=email, password=password)


@pytest_asyncio.fixture(name='superuser')
async def fixture_superuser(db_session: AsyncSession, superuser_role: Role) -> Iterator[TestUser]:
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
    yield TestUser(email=email, password=password)


def _hash_password(salt: str, password: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
