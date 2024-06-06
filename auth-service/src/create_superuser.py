import asyncio
import hashlib
import uuid
from functools import wraps

import typer

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from models.entity import User, Role, user_role
from core.config import settings

SUPERUSER = 'superuser'

app = typer.Typer()


def coro(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


@app.command()
@coro
async def create_superuser():
    email = input('Enter email: ')
    password = input('Enter password: ')
    salt = email.encode('utf-8')
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()

    dsn = (f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@'
           f'{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}')
    engine = create_async_engine(dsn, echo=False, future=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    Base = declarative_base()

    async with async_session() as session:
        user_id = uuid.uuid4()
        await session.execute(insert(User).values(id=user_id, email=email, hashed_password=hashed_password))

        role = await session.execute(select(Role).where(Role.name == SUPERUSER))
        role = role.scalars().all()
        message = ''  # pylint: disable=invalid-name
        if not role:
            role_id = uuid.uuid4()
            await session.execute(insert(Role).values(id=role_id, name=SUPERUSER))
            message = f'added role superuser with id = {role_id}\n'
        else:
            role_id = role[0].id
        await session.execute(
            insert(user_role)
            .values(user_id=user_id, role_id=role_id))
        await session.commit()
        message += f'added superuser with id = {user_id}'
        print(message)


if __name__ == "__main__":
    create_superuser()
