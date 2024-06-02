from uuid import uuid4
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.entity import User
from services.password_service import PasswordService, get_password_service


class UserService:
    def __init__(self, db_session: AsyncSession, password_service: PasswordService):
        self._db_session = db_session
        self._password_service = password_service

    async def get_by_id(self, user_id: str) -> User | None:
        return await self._db_session.scalar(select(User).where(User.id == user_id))

    async def get_by_email(self, email: str) -> User | None:
        return await self._db_session.scalar(select(User).where(User.email == email))

    async def create(self, email: str, password: str) -> User:
        hashed_password = self._password_service.get_password_hash(email, password)
        user = User(id=uuid4(), email=email, hashed_password=hashed_password)
        self._db_session.add(user)
        await self._db_session.commit()
        return user


def get_user_service(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
) -> UserService:
    return UserService(db_session, password_service)
