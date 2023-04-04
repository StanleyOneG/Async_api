from functools import lru_cache
from core.config import CACHE_SERVICE_NAME
from cache.abstract_cache import AbstractBaseCache
from db.redis import get_redis

@lru_cache
def get_cache_service():
    if CACHE_SERVICE_NAME == 'redis':
         return RedisCache()


class RedisCache(AbstractBaseCache):
    """Interface for Redis cache service"""

    def __init__(self) -> None:
        self.redis = get_redis()

    async def get(self, key):
        return await self.redis.get(key)

    async def set(self, key, value, expire):
        return await self.redis.set(key, value, expire)