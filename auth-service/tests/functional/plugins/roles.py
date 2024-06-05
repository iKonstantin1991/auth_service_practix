from typing import Iterator
from uuid import uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.functional.plugins.models import Role


@pytest_asyncio.fixture(scope='session', name='superuser_role')
async def fixture_superuser_role(db_session: AsyncSession) -> Iterator[Role]:
    superuser_role = Role(id=uuid4(), name='superuser')
    db_session.add(superuser_role)
    await db_session.commit()
    yield superuser_role


@pytest_asyncio.fixture(name='role')
async def fixture_role(db_session: AsyncSession) -> Iterator[Role]:
    role = Role(id=uuid4(), name=str(uuid4()))
    db_session.add(role)
    await db_session.commit()
    yield role
