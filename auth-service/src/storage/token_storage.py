from uuid import UUID
import logging

from redis import RedisError
from redis.asyncio import Redis

_REFRESH_PREFIX = 'refresh'
_ACCESS_PREFIX = 'access'

logger = logging.getLogger(__name__)


class TokenStorage:
    cache_storage: Redis

    async def save_refresh_token(self, refresh_token: str, user_id: UUID):
        try:
            await self.cache_storage.set(self._refresh_cache_key(user_id), refresh_token)
        except RedisError as e:
            logger.error('Failed to save refresh token %s in cache: %s', refresh_token, e)

    async def delete_refresh_token(self, refresh_token: str, user_id: UUID):
        try:
            await self.cache_storage.delete(self._refresh_cache_key(user_id))
        except RedisError as e:
            logger.error('Failed to delete refresh token %s from cache: %s', refresh_token, e)

    async def save_access_token(self, access_token: str, user_id: UUID):
        try:
            await self.cache_storage.set(self._access_cache_key(user_id), access_token)
        except RedisError as e:
            logger.error('Failed to save access token %s in cache: %s', access_token, e)

    async def check_login(self, access_token: str, user_id: UUID):
        try:
            access_token = await self.cache_storage.get(self._access_cache_key(user_id))
        except RedisError as e:
            logger.error('Failed to check access token %s in cache% %s', access_token, e)

        if not access_token:
            return True
        return False

    @staticmethod
    def _refresh_cache_key(user_id: UUID) -> str:
        return f'{_REFRESH_PREFIX}:{user_id}'

    @staticmethod
    def _access_cache_key(user_id: UUID) -> str:
        return f'{_ACCESS_PREFIX}:{user_id}'
