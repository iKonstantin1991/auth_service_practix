import logging
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from redis import RedisError
from redis.asyncio import Redis

from db.redis import get_redis

_REFRESH_PREFIX = 'refresh'
_ACCESS_PREFIX = 'access'
_TOKEN_KEY = 'token_key'

logger = logging.getLogger(__name__)


class TokenStorage:
    def __init__(self, cache_storage: Redis):
        self.cache_storage = cache_storage

    async def save_refresh_jti(self, jti: UUID, ttl: int) -> None:
        logger.info('Saving refresh jti %s in cache', jti)
        try:
            await self.cache_storage.set(self._refresh_jti_cache_key(jti), _TOKEN_KEY, ttl)
        except RedisError as e:
            logger.error('Failed to save refresh jti %s in cache: %s', jti, e)
            raise

    async def remove_refresh_jti(self, jti: UUID) -> None:
        logger.info('Removing refresh jti %s from cache', jti)
        try:
            await self.cache_storage.delete(self._refresh_jti_cache_key(jti))
        except RedisError as e:
            logger.error('Failed to remove refresh jti %s from cache: %s', jti, e)
            raise

    async def check_refresh_token_exists(self, jti: UUID) -> bool:
        logger.info('Checking if refresh jti %s exists in cache', jti)
        try:
            jti = await self.cache_storage.getdel(self._refresh_jti_cache_key(jti))
            return jti is not None
        except RedisError as e:
            logger.error('Failed to delete refresh jti %s from cache: %s', jti, e)
            raise

    async def save_revoked_access_jti(self, jti: UUID, ttl: int) -> None:
        logger.info('Saving revoked access jti %s in cache', jti)
        try:
            await self.cache_storage.set(self._revoked_access_jti_cache_key(jti), _TOKEN_KEY, ttl)
        except RedisError as e:
            logger.error('Failed to save revoked access jti %s in cache: %s', jti, e)
            raise

    async def check_access_token_revoked(self, jti: UUID) -> bool:
        logger.info('Checking if access token with jti %s was revoked in cache', jti)
        try:
            is_exist = await self.cache_storage.exists(self._revoked_access_jti_cache_key(jti))
            return bool(is_exist)
        except RedisError as e:
            logger.error('Failed to check if access token with jti %s is revoked in cache %s', jti, e)
            raise

    @staticmethod
    def _refresh_jti_cache_key(jti: UUID) -> str:
        return f'{_REFRESH_PREFIX}:{jti}'

    @staticmethod
    def _revoked_access_jti_cache_key(jti: UUID) -> str:
        return f'{_ACCESS_PREFIX}:revoked:{jti}'


@lru_cache()
def get_token_storage(
    cache_storage: Annotated[Redis, Depends(get_redis)]
) -> TokenStorage:
    return TokenStorage(cache_storage)
