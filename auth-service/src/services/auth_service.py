import logging
import time
from typing import Annotated, List
from uuid import uuid4, UUID
from datetime import datetime
from enum import Enum

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from fastapi import Depends

from db.postgres import get_session
from core.config import settings
from models.entity import UserLogin
from services.password_service import PasswordService, get_password_service
from storage.token_storage import TokenStorage, get_token_storage

_ALGORITHM = "HS256"
_ACCESS_TOKEN_EXPIRE_SECONDS = 24 * 60 * 60  # 1 day
_REFRESH_TOKEN_EXPIRE_SECONDS = 10 * 24 * 60 * 60  # 10 days

logger = logging.getLogger(__name__)


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayload(BaseModel):
    user_id: UUID
    type: TokenType
    iat: float = Field(default_factory=time.time)
    exp: float

    def dict(self, *args, **kwargs) -> dict:
        data = super().dict(*args, **kwargs)
        data["user_id"] = str(data["user_id"])
        return data


class AuthService:
    def __init__(
        self, db_session: AsyncSession, token_storage: TokenStorage, password_service: PasswordService
    ) -> None:
        self._db_session = db_session
        self._token_storage = token_storage
        self._password_service = password_service

    def create_access_token(self, user_id: UUID) -> str:
        logger.info('Creating access token for user %s', user_id)
        payload = TokenPayload(
            user_id=user_id,
            type=TokenType.ACCESS,
            exp=time.time() + _ACCESS_TOKEN_EXPIRE_SECONDS
        )
        return self._create_token(payload)

    async def create_refresh_token(self, user_id: UUID) -> str:
        logger.info('Creating refresh token for user %s', user_id)
        payload = TokenPayload(
            user_id=user_id,
            type=TokenType.REFRESH,
            exp=time.time() + _REFRESH_TOKEN_EXPIRE_SECONDS,
        )
        token = self._create_token(payload)
        await self._token_storage.save_refresh_token(token, _REFRESH_TOKEN_EXPIRE_SECONDS)
        return token


    def verify_password(self, user_email: str, plain_password: str, hashed_password: str) -> bool:
        logger.info('Verifying password for user with email %s', user_email)
        return self._password_service.verify_password(user_email, plain_password, hashed_password)

    async def is_access_token_invalid(self, access_token: str) -> bool:
        logger.info('Checking if access token is invalid')
        try:
            payload = self._decode_token(access_token)
        except jwt.exceptions.InvalidTokenError as e:
            logger.info('Access token is invalid: %s', e)
            return True
        if payload.type != TokenType.ACCESS:
            logger.info('Access token is not of type access')
            return True
        return await self._token_storage.check_access_token_revoked(access_token)

    async def is_refresh_token_invalid(self, refresh_token: str) -> bool:
        logger.info('Checking if refresh token is invalid')
        try:
            payload = self._decode_token(refresh_token)
        except jwt.exceptions.InvalidTokenError as e:
            logger.info('Refresh token is invalid: %s', e)
            return True
        if payload.type != TokenType.REFRESH:
            logger.info('Refresh token is not of type refresh')
            return True
        return not await self._token_storage.check_refresh_token_exists(refresh_token)

    async def invalidate_access_token(self, access_token: str) -> None:
        logger.info('Invalidating access token')
        ttl = int(self._decode_token(access_token).exp - time.time())
        await self._token_storage.save_revoked_access_token(access_token, ttl)

    def get_user_id(self, access_token: str) -> UUID:
        payload = self._decode_token(access_token)
        return payload.user_id

    async def get_history(self, user_id: UUID) -> List[UserLogin]:
        logger.info('Getting auth history for user %s', user_id)
        return await self._db_session.scalars(select(UserLogin)
                                              .where(UserLogin.user_id == user_id)
                                              .order_by(UserLogin.date))

    async def update_history(self, user_id: UUID, user_agent: str | None) -> UserLogin:
        logger.info('Updating auth history for user %s, user agent: %s', user_id, user_agent)
        user_login = UserLogin(id=uuid4(), user_agent=user_agent, user_id=user_id, date=datetime.utcnow())
        self._db_session.add(user_login)
        await self._db_session.commit()
        return user_login

    def _create_token(self, payload: TokenPayload) -> str:
        return jwt.encode(payload.dict(), settings.secret_key, algorithm=_ALGORITHM)

    def _decode_token(self, token: str) -> TokenPayload:
        return TokenPayload(**jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM]))


def get_auth_service(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    token_storage: Annotated[TokenStorage, Depends(get_token_storage)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
) -> AuthService:
    return AuthService(db_session, token_storage, password_service)
