from typing import Iterator, List
from uuid import uuid4, UUID
import hashlib

import pytest_asyncio
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from tests.functional.plugins.models import User, Role
from tests.functional.plugins.roles import TestRole


class TestUser(BaseModel):
    __test__ = False

    email: str
    password: str


class TestUserWithRoles(BaseModel):
    __test__ = False

    email: str
    password: str
    roles: List[TestRole]


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
    yield TestUser(id=user_id, email=email, password=password)


@pytest_asyncio.fixture(name='user_with_usual_role')
async def fixture_user_with_usual_role(db_session, usual_user_role) -> Iterator[TestUserWithRoles]:
    user_id = uuid4()
    email = f'{uuid4()}@test.com'
    password = 'password'
    user = User(
        id=user_id,
        email=email,
        hashed_password=_hash_password(email, password),
        roles=[usual_user_role],
    )
    db_session.add(user)
    await db_session.commit()
    yield usual_user_role


def _hash_password(salt: str, password: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
