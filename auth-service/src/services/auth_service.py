import logging
import time
from typing import Annotated, List
from uuid import uuid4, UUID
from datetime import datetime
from enum import Enum

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ValidationError
from fastapi import Depends
from fastapi_pagination.ext.sqlalchemy import paginate

from db.postgres import get_session
from core.config import settings
from models.entity import UserLogin, Role
from services.password_service import PasswordService, get_password_service
from storage.token_storage import TokenStorage, get_token_storage

_ALGORITHM = "RS256"
_ACCESS_TOKEN_EXPIRE_SECONDS = 24 * 60 * 60  # 1 day
_REFRESH_TOKEN_EXPIRE_SECONDS = 10 * 24 * 60 * 60  # 10 days

logger = logging.getLogger(__name__)


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class BaseTokenPayload(BaseModel):
    user_id: UUID
    type: TokenType
    iat: float = Field(default_factory=time.time)
    exp: float
    jti: UUID = Field(default_factory=uuid4)

    def model_dump(self, *args, **kwargs) -> dict:
        data = super().model_dump(*args, **kwargs)
        data["user_id"] = str(data["user_id"])
        data["jti"] = str(data["jti"])
        return data


class AccessTokenPayload(BaseTokenPayload):
    type: TokenType = TokenType.ACCESS
    exp: float = Field(default_factory=lambda: time.time() + _ACCESS_TOKEN_EXPIRE_SECONDS)
    roles: List[str]


class RefreshTokenPayload(BaseTokenPayload):
    type: TokenType = TokenType.REFRESH
    exp: float = Field(default_factory=lambda: time.time() + _REFRESH_TOKEN_EXPIRE_SECONDS)
    access_jti: UUID

    def model_dump(self, *args, **kwargs) -> dict:
        data = super().model_dump(*args, **kwargs)
        data["access_jti"] = str(data["access_jti"])
        return data


class AuthService:
    def __init__(
        self, db_session: AsyncSession, token_storage: TokenStorage, password_service: PasswordService
    ) -> None:
        self._db_session = db_session
        self._token_storage = token_storage
        self._password_service = password_service

    async def create_token_pair(self, user_id: UUID, roles: List[Role]) -> tuple[str, str]:
        logger.info('Creating token pair for user %s', user_id)
        access_token_payload = AccessTokenPayload(user_id=user_id, roles=[r.name for r in roles])
        refresh_token_payload = RefreshTokenPayload(user_id=user_id, access_jti=access_token_payload.jti)
        access_token = self._create_token(access_token_payload)
        refresh_token = self._create_token(refresh_token_payload)
        await self._token_storage.save_refresh_jti(refresh_token_payload.jti, _REFRESH_TOKEN_EXPIRE_SECONDS)
        return access_token, refresh_token

    def verify_password(self, user_email: str, plain_password: str, hashed_password: str) -> bool:
        logger.info('Verifying password for user with email %s', user_email)
        return self._password_service.verify_password(user_email, plain_password, hashed_password)

    async def is_access_token_valid(self, access_token: str) -> bool:
        logger.info('Checking if access token is valid')
        try:
            payload = self._decode_access_token(access_token)
        except (jwt.exceptions.InvalidTokenError, ValidationError) as e:
            logger.info('Access token is invalid: %s', e)
            return False
        if payload.type != TokenType.ACCESS:
            logger.info('Access token is not of type access')
            return False
        return not await self._token_storage.check_access_token_revoked(payload.jti)

    async def check_is_valid_and_remove_refresh_token(self, refresh_token: str) -> bool:
        logger.info('Checking if refresh token is valid and remove')
        try:
            payload = self._decode_refresh_token(refresh_token)
        except (jwt.exceptions.InvalidTokenError, ValidationError) as e:
            logger.info('Refresh token is invalid: %s', e)
            return False
        if payload.type != TokenType.REFRESH:
            logger.info('Refresh token is not of type refresh')
            return False
        return await self._token_storage.check_refresh_token_exists(payload.jti)

    async def logout(self, refresh_token: str) -> None:
        payload = self._decode_refresh_token(refresh_token)
        logger.info('Revoking refresh token with jti %s and access token with jti %s', payload.jti, payload.access_jti)
        await self._token_storage.remove_refresh_jti(payload.jti)
        # access token is issued at the same time as refresh token
        access_token_ttl = int(payload.iat + _ACCESS_TOKEN_EXPIRE_SECONDS - time.time())
        if access_token_ttl > 0:
            await self._token_storage.save_revoked_access_jti(payload.access_jti, access_token_ttl)

    def get_user_id_from_access_token(self, token: str) -> UUID:
        payload = self._decode_access_token(token)
        return payload.user_id

    def get_user_id_from_refresh_token(self, token: str) -> UUID:
        payload = self._decode_refresh_token(token)
        return payload.user_id

    async def get_history(self, user_id: UUID) -> List[UserLogin]:
        logger.info('Getting auth history for user %s', user_id)
        return await paginate(self._db_session,
                              select(UserLogin).where(UserLogin.user_id == user_id)
                                               .order_by(UserLogin.date.desc()))

    async def update_history(self, user_id: UUID, user_agent: str | None) -> UserLogin:
        logger.info('Updating auth history for user %s, user agent: %s', user_id, user_agent)
        user_login = UserLogin(id=uuid4(), user_agent=user_agent, user_id=user_id, date=datetime.utcnow())
        self._db_session.add(user_login)
        await self._db_session.commit()
        return user_login

    def _create_token(self, payload: BaseTokenPayload) -> str:
        return jwt.encode(payload.dict(), settings.private_key, algorithm=_ALGORITHM)

    def _decode_access_token(self, token: str) -> AccessTokenPayload:
        return AccessTokenPayload(**jwt.decode(token, settings.public_key, algorithms=[_ALGORITHM]))

    def _decode_refresh_token(self, token: str) -> RefreshTokenPayload:
        return RefreshTokenPayload(**jwt.decode(token, settings.public_key, algorithms=[_ALGORITHM]))


def get_auth_service(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    token_storage: Annotated[TokenStorage, Depends(get_token_storage)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
) -> AuthService:
    return AuthService(db_session, token_storage, password_service)
