from typing import Iterator, List
from uuid import uuid4, UUID
import hashlib
from dataclasses import dataclass

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.functional.plugins.models import User, Role


@dataclass(frozen=True)
class TestUser:
    __test__ = False

    id: UUID
    email: str
    password: str
    roles: List[Role]


@pytest_asyncio.fixture(name='user')
async def fixture_user(db_session: AsyncSession) -> Iterator[TestUser]:
    id, email, password = uuid4(), f'{uuid4()}@test.com', 'password'
    roles = [Role(id=uuid4(), name=str(uuid4()))]
    user = User(
        id=id,
        email=email,
        hashed_password=_hash_password(email, password),
        roles=roles,
    )
    db_session.add(user)
    await db_session.commit()
    yield TestUser(id=id, email=email, password=password, roles=roles)


@pytest_asyncio.fixture(name='superuser')
async def fixture_superuser(
    db_session: AsyncSession, superuser_role: Role
) -> Iterator[TestUser]:
    id, email, password = uuid4(), f'{uuid4()}@test.com', 'password'
    user = User(
        id=id,
        email=email,
        hashed_password=_hash_password(email, password),
        roles=[superuser_role],
    )
    db_session.add(user)
    await db_session.commit()
    yield TestUser(
        id=id, email=email, password=password, roles=[superuser_role]
    )


def _hash_password(salt: str, password: str) -> str:
    return hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000
    ).hex()
