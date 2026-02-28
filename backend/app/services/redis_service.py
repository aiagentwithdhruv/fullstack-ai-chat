import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()

_redis: redis.Redis | None = None


async def connect_redis():
    global _redis
    try:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
        await _redis.ping()
    except Exception:
        _redis = None


async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()


async def ping_redis() -> bool:
    try:
        if _redis is None:
            return False
        return await _redis.ping()
    except Exception:
        return False


async def check_rate_limit(client_ip: str) -> bool:
    """Returns True if request is allowed, False if rate limited."""
    if _redis is None:
        return True  # Skip rate limiting if Redis unavailable

    key = f"rate:{client_ip}"
    count = await _redis.get(key)
    if count and int(count) >= settings.rate_limit_per_minute:
        return False

    pipe = _redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, 60)
    await pipe.execute()
    return True


async def cache_get(key: str) -> str | None:
    if _redis is None:
        return None
    return await _redis.get(key)


async def cache_set(key: str, value: str, ttl: int = 300):
    if _redis is None:
        return
    await _redis.set(key, value, ex=ttl)
