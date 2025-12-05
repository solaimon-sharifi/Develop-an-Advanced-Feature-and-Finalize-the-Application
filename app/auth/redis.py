# app/auth/redis.py
"""Redis helpers used by the authentication layer."""

import logging
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

try:
    import aioredis

    _aioredis_error: Optional[BaseException] = None
    _aioredis_available = True
except Exception as exc:
    aioredis = None  # type: ignore[assignment]
    _aioredis_error = exc
    _aioredis_available = False
    logger.warning("Redis client unavailable: %s", exc)


async def _ensure_redis() -> "aioredis.Redis":
    if not _aioredis_available:
        raise RuntimeError(
            "Redis support (aioredis) is unavailable"
        ) from (_aioredis_error or None)

    if not hasattr(_ensure_redis, "redis"):
        _ensure_redis.redis = await aioredis.from_url(
            settings.REDIS_URL or "redis://localhost"
        )
    return _ensure_redis.redis


async def get_redis():
    """Return the cached aioredis client."""
    return await _ensure_redis()


async def add_to_blacklist(jti: str, exp: int):
    """Add a token's JTI to the blacklist."""
    if not _aioredis_available:
        logger.debug("Skipping blacklist write; redis unavailable.")
        return

    redis = await _ensure_redis()
    await redis.set(f"blacklist:{jti}", "1", ex=exp)


async def is_blacklisted(jti: str) -> bool:
    """Check if a token's JTI is blacklisted."""
    if not _aioredis_available:
        logger.debug("Redis unavailable; treating token as not blacklisted.")
        return False

    redis = await _ensure_redis()
    return await redis.exists(f"blacklist:{jti}")