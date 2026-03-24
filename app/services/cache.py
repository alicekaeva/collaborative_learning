import json
from typing import Optional, Any
import redis.asyncio as aioredis

from app.core.config import settings

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


async def get_cached(key: str) -> Optional[Any]:
    r = await get_redis()
    data = await r.get(key)
    if data:
        return json.loads(data)
    return None


async def set_cached(key: str, value: Any, ttl: int = settings.RECOMMENDATIONS_CACHE_TTL) -> None:
    r = await get_redis()
    await r.setex(key, ttl, json.dumps(value))


async def delete_cached(key: str) -> None:
    r = await get_redis()
    await r.delete(key)


async def store_refresh_token(user_id: int, token: str) -> None:
    r = await get_redis()
    ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    await r.setex(f"refresh:{token}", ttl, str(user_id))


async def validate_refresh_token(token: str) -> Optional[int]:
    r = await get_redis()
    user_id = await r.get(f"refresh:{token}")
    return int(user_id) if user_id else None


async def revoke_refresh_token(token: str) -> None:
    r = await get_redis()
    await r.delete(f"refresh:{token}")
