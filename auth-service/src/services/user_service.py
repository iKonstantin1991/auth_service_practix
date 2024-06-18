import logging
from uuid import uuid4, UUID
from typing import Annotated, List

from aiohttp import ClientSession
from fastapi import Depends
from sqlalchemy import select, update, insert, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from http_client import get_session as get_http_session
from core.config import settings
from models.entity import User, YandexUser, Role, user_role
from services.password_service import PasswordService, get_password_service


logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        db_session: AsyncSession,
        password_service: PasswordService,
        http_session: ClientSession,
    ) -> None:
        self._db_session = db_session
        self._password_service = password_service
        self._http_session = http_session

    async def get_by_id(self, user_id: UUID) -> User | None:
        logger.info('Getting user by id: %s', user_id)
        return await self._db_session.scalar(
            select(User)
            .where(User.id == user_id)
            .options(joinedload(User.roles))
        )

    async def get_by_email(self, email: str) -> User | None:
        logger.info('Getting user by email: %s', email)
        return await self._db_session.scalar(
            select(User)
            .where(User.email == email)
            .options(joinedload(User.roles))
        )

    async def create(self, email: str, password: str) -> User:
        logger.info('Creating user with email: %s', email)
        hashed_password = self._password_service.get_password_hash(
            email, password
        )
        user = User(id=uuid4(), email=email, hashed_password=hashed_password)
        self._db_session.add(user)
        await self._db_session.commit()
        return user

    async def get_or_create_from_yandex(self, code: str) -> User:
        logger.info('Getting or creating user from yandex')
        token = await self._get_yandex_user_data_access_token(code)
        user_info = await self._get_yandex_user_info_by_token(token)
        yandex_user_id, email = user_info['id'], user_info['default_email']
        yandex_user = await self._db_session.scalar(
            select(YandexUser).where(YandexUser.id == yandex_user_id)
        )
        if yandex_user:
            logger.info('Yandex user found, id: %s', yandex_user_id)
            user = await self.get_by_id(yandex_user.user_id)
            return user
        logger.info(
            'Yandex user with id %s not found, creating new user',
            yandex_user_id,
        )
        hashed_password = self._password_service.get_password_hash(
            email, str(uuid4())
        )
        user = User(
            id=uuid4(), email=email, hashed_password=hashed_password, roles=[]
        )
        yandex_user = YandexUser(id=yandex_user_id, user_id=user.id)
        self._db_session.add(user)
        self._db_session.add(yandex_user)
        await self._db_session.commit()
        return user

    async def get_roles(self, user_id: UUID) -> List[Role]:
        logger.info('Getting user roles, user_id = %s', user_id)
        user_roles_names = await self._db_session.execute(
            select(Role.id, Role.name)
            .join(user_role, Role.id == user_role.c.role_id)
            .where(user_role.c.user_id == user_id)
        )
        user_roles_names = [
            Role(id=row[0], name=row[1]) for row in user_roles_names
        ]
        return user_roles_names

    async def update(self, user_id: UUID, email: str, password: str) -> User:
        logger.info('Updating user with id = %s', user_id)
        hashed_password = self._password_service.get_password_hash(
            email, password
        )
        updated_user = await self._db_session.execute(
            update(User)
            .where(User.id == user_id)
            .values(email=email, hashed_password=hashed_password)
            .returning(User)
        )
        await self._db_session.commit()
        return updated_user.scalar()

    async def has_role(self, user_id: UUID, role_id: UUID):
        logger.info(
            'Checking if user with id = %s have role with id = %s',
            user_id,
            role_id,
        )
        return await self._db_session.scalar(
            select(user_role).where(
                user_role.c.user_id == user_id, user_role.c.role_id == role_id
            )
        )

    async def add_role_to_user(self, user_id: UUID, role_id: UUID) -> UUID:
        logger.info(
            'Adding role with id = %s to user with id = %s', role_id, user_id
        )
        role_id = await self._db_session.execute(
            insert(user_role)
            .values(user_id=user_id, role_id=role_id)
            .returning(user_role.c.role_id)
        )
        await self._db_session.commit()
        role_id = UUID(str(role_id.scalar()))
        return role_id

    async def delete_role_from_user(
        self, user_id: UUID, role_id: UUID
    ) -> None:
        logger.info(
            'Deleting role with id = %s from user with id = %s',
            role_id,
            user_id,
        )
        await self._db_session.execute(
            delete(user_role).where(
                user_role.c.user_id == user_id, user_role.c.role_id == role_id
            )
        )
        await self._db_session.commit()

    async def _get_yandex_user_data_access_token(self, code: str) -> str:
        logger.info('Getting user data access token')
        async with self._http_session.post(
            'https://oauth.yandex.ru/token',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': settings.yandex_client_id,
                'client_secret': settings.yandex_client_secret,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            raise_for_status=True,
        ) as response:
            return (await response.json())['access_token']

    async def _get_yandex_user_info_by_token(self, token: str) -> dict:
        logger.info('Getting user info by token')
        async with self._http_session.get(
            'https://login.yandex.ru/info',
            headers={'Authorization': f'OAuth {token}'},
        ) as response:
            return await response.json()


def get_user_service(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    password_service: Annotated[
        PasswordService, Depends(get_password_service)
    ],
    http_session: Annotated[ClientSession, Depends(get_http_session)],
) -> UserService:
    return UserService(db_session, password_service, http_session)
