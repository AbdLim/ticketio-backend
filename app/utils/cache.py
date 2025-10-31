# RedisCache class for caching with functions (set, get, remove) -> cache
from typing import Any, Optional, AsyncGenerator
import json
from redis.asyncio import Redis
from redis.exceptions import RedisError
from app.core.config import Settings

settings = Settings()


class RedisCache:
    def __init__(self):
        self._client: Optional[Redis] = None

    async def get_client(self) -> Redis:
        if self._client is None:
            self._client = Redis.from_url(
                str(settings.REDIS_URL),
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True,
            )
        return self._client

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        try:
            client = await self.get_client()
            if not isinstance(value, (str, int, float)):
                value = json.dumps(value)
            return await client.set(key, value, ex=expire)
        except RedisError:
            return False

    async def get(self, key: str, default: Any = None) -> Any:
        try:
            client = await self.get_client()
            value = await client.get(key)
            if value is None:
                return default
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except RedisError:
            return default

    async def delete(self, key: str) -> bool:
        try:
            client = await self.get_client()
            return bool(await client.delete(key))
        except RedisError:
            return False

    async def exists(self, key: str) -> bool:
        try:
            client = await self.get_client()
            return bool(await client.exists(key))
        except RedisError:
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        try:
            client = await self.get_client()
            return bool(await client.expire(key, seconds))
        except RedisError:
            return False

    async def ttl(self, key: str) -> int:
        try:
            client = await self.get_client()
            return await client.ttl(key)
        except RedisError:
            return -1

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None


# Global Redis cache instance
_redis_cache: Optional[RedisCache] = None


def get_redis_cache() -> RedisCache:
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
    return _redis_cache


async def get_cache() -> AsyncGenerator[RedisCache, None]:
    """FastAPI dependency for getting Redis cache instance"""
    cache = get_redis_cache()
    try:
        yield cache
    finally:
        await cache.close()


# Create a global cache instance for direct usage
cache = get_redis_cache()
