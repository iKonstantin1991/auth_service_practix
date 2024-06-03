import logging
from functools import lru_cache
from typing import Annotated

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

    async def save_refresh_token(self, refresh_token: str, ttl: int) -> None:
        logger.info('Saving refresh token in cache')
        try:
            await self.cache_storage.set(self._refresh_cache_key(refresh_token), _TOKEN_KEY, ttl)
        except RedisError as e:
            logger.error('Failed to save refresh token %s in cache: %s', refresh_token, e)
            raise

    async def check_refresh_token_exists(self, refresh_token: str) -> bool:
        logger.info('Checking if refresh token exists in cache')
        try:
            token = await self.cache_storage.getdel(self._refresh_cache_key(refresh_token))
            return token is not None
        except RedisError as e:
            logger.error('Failed to delete refresh token %s from cache: %s', refresh_token, e)
            raise

    async def save_revoked_access_token(self, access_token: str, ttl: int) -> None:
        logger.info('Saving revoked access token in cache')
        try:
            await self.cache_storage.set(self._revoked_access_cache_key(access_token), _TOKEN_KEY, ttl)
        except RedisError as e:
            logger.error('Failed to save revoked access token %s in cache: %s', access_token, e)
            raise

    async def check_access_token_revoked(self, access_token: str) -> bool:
        logger.info('Checking if access token was revoked in cache')
        try:
            is_exist = await self.cache_storage.exists(self._revoked_access_cache_key(access_token))
            return bool(is_exist)
        except RedisError as e:
            logger.error('Failed to check if access token %s is revoked in cache %s', access_token, e)
            raise

    @staticmethod
    def _refresh_cache_key(refresh_token: str) -> str:
        return f'{_REFRESH_PREFIX}:{refresh_token}'

    @staticmethod
    def _revoked_access_cache_key(access_token: str) -> str:
        return f'{_ACCESS_PREFIX}:revoked:{access_token}'


@lru_cache()
def get_token_storage(
    cache_storage: Annotated[Redis, Depends(get_redis)]
) -> TokenStorage:
    return TokenStorage(cache_storage)
