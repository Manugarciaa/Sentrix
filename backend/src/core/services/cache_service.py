"""
Redis Cache Service for Sentrix Backend
Provides caching functionality with automatic fallback if Redis is unavailable
"""
import json
import hashlib
from typing import Any, Optional, Callable, Dict
from functools import wraps
import asyncio
from datetime import timedelta

from ...logging_config import get_logger

logger = get_logger(__name__)

# Try to import Redis, but don't fail if not available
try:
    import redis.asyncio as redis
    from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis_not_installed", message="Redis package not installed. Caching will be disabled.")


class CacheService:
    """
    Redis cache service with automatic fallback

    Features:
    - Automatic connection management
    - JSON serialization
    - TTL support
    - Key prefixing
    - Graceful degradation if Redis unavailable
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 300,  # 5 minutes
        key_prefix: str = "sentrix",
        enabled: bool = True
    ):
        """
        Initialize cache service

        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds (5 minutes)
            key_prefix: Prefix for all cache keys
            enabled: Whether caching is enabled
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.enabled = enabled and REDIS_AVAILABLE
        self._client: Optional[redis.Redis] = None
        self._connection_failed = False

        if not REDIS_AVAILABLE:
            logger.warning("cache_disabled", reason="Redis not available")
        elif not enabled:
            logger.info("cache_disabled", reason="Disabled in configuration")

    async def _get_client(self) -> Optional[redis.Redis]:
        """Get Redis client with lazy connection"""
        if not self.enabled or self._connection_failed:
            return None

        if self._client is None:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                await self._client.ping()
                logger.info("cache_connected", redis_url=self.redis_url[:30] + "...")
            except Exception as e:
                logger.error("cache_connection_failed", error=str(e), redis_url=self.redis_url[:30] + "...")
                self._connection_failed = True
                return None

        return self._client

    def _make_key(self, key: str) -> str:
        """Create prefixed cache key"""
        return f"{self.key_prefix}:{key}"

    def _hash_dict(self, data: Dict) -> str:
        """Create hash from dictionary for cache key"""
        # Sort dict to ensure consistent hashing
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()[:12]

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key (will be prefixed)

        Returns:
            Cached value or None if not found/error
        """
        client = await self._get_client()
        if not client:
            return None

        try:
            full_key = self._make_key(key)
            value = await client.get(full_key)

            if value is None:
                logger.debug("cache_miss", key=key)
                return None

            logger.debug("cache_hit", key=key)
            return json.loads(value)

        except (RedisError, RedisConnectionError, json.JSONDecodeError) as e:
            logger.error("cache_get_error", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key (will be prefixed)
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: 300)

        Returns:
            True if successful, False otherwise
        """
        client = await self._get_client()
        if not client:
            return False

        try:
            full_key = self._make_key(key)
            ttl = ttl or self.default_ttl

            # Serialize to JSON
            json_value = json.dumps(value)

            # Set with TTL
            await client.setex(full_key, ttl, json_value)

            logger.debug("cache_set", key=key, ttl=ttl)
            return True

        except (RedisError, RedisConnectionError, TypeError, ValueError) as e:
            logger.error("cache_set_error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key (will be prefixed)

        Returns:
            True if successful, False otherwise
        """
        client = await self._get_client()
        if not client:
            return False

        try:
            full_key = self._make_key(key)
            await client.delete(full_key)
            logger.debug("cache_delete", key=key)
            return True

        except (RedisError, RedisConnectionError) as e:
            logger.error("cache_delete_error", key=key, error=str(e))
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Pattern to match (e.g., "analyses:*")

        Returns:
            Number of keys deleted
        """
        client = await self._get_client()
        if not client:
            return 0

        try:
            full_pattern = self._make_key(pattern)

            # Get all matching keys
            keys = []
            async for key in client.scan_iter(match=full_pattern, count=100):
                keys.append(key)

            if keys:
                deleted = await client.delete(*keys)
                logger.debug("cache_delete_pattern", pattern=pattern, deleted=deleted)
                return deleted

            return 0

        except (RedisError, RedisConnectionError) as e:
            logger.error("cache_delete_pattern_error", pattern=pattern, error=str(e))
            return 0

    async def clear_all(self) -> bool:
        """
        Clear all cache keys (use with caution!)

        Returns:
            True if successful, False otherwise
        """
        client = await self._get_client()
        if not client:
            return False

        try:
            await client.flushdb()
            logger.warning("cache_cleared", message="All cache keys deleted")
            return True

        except (RedisError, RedisConnectionError) as e:
            logger.error("cache_clear_error", error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        client = await self._get_client()
        if not client:
            return False

        try:
            full_key = self._make_key(key)
            exists = await client.exists(full_key)
            return bool(exists)

        except (RedisError, RedisConnectionError) as e:
            logger.error("cache_exists_error", key=key, error=str(e))
            return False

    async def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for key in seconds"""
        client = await self._get_client()
        if not client:
            return None

        try:
            full_key = self._make_key(key)
            ttl = await client.ttl(full_key)
            return ttl if ttl > 0 else None

        except (RedisError, RedisConnectionError) as e:
            logger.error("cache_ttl_error", key=key, error=str(e))
            return None

    async def health_check(self) -> Dict[str, Any]:
        """
        Check cache service health

        Returns:
            Health status dict
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "redis_available": REDIS_AVAILABLE,
                "message": "Caching is disabled"
            }

        client = await self._get_client()
        if not client:
            return {
                "status": "unhealthy",
                "redis_available": REDIS_AVAILABLE,
                "connection_failed": self._connection_failed,
                "message": "Cannot connect to Redis"
            }

        try:
            # Ping test
            await client.ping()

            # Get info
            info = await client.info("stats")

            return {
                "status": "healthy",
                "redis_available": True,
                "redis_url": self.redis_url[:30] + "...",
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "connected_clients": info.get("connected_clients", 0)
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "redis_available": REDIS_AVAILABLE,
                "error": str(e)
            }

    async def close(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("cache_connection_closed")


# Decorator for caching function results
def cached(
    key_func: Callable = None,
    ttl: int = 300,
    key_prefix: str = "",
    cache_service: Optional[CacheService] = None
):
    """
    Decorator to cache function results

    Usage:
        @cached(key_func=lambda user_id, filters: f"analyses:list:{user_id}:{hash(filters)}", ttl=300)
        async def list_analyses(user_id: str, filters: dict):
            # Function implementation
            pass

    Args:
        key_func: Function to generate cache key from args
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache key
        cache_service: Cache service instance (will use global if None)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache service (use global or provided)
            service = cache_service or get_cache_service()

            if not service or not service.enabled:
                # No caching, execute function directly
                return await func(*args, **kwargs)

            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: use function name and args hash
                args_str = f"{args}_{kwargs}"
                args_hash = hashlib.md5(args_str.encode()).hexdigest()[:12]
                cache_key = f"{func.__name__}:{args_hash}"

            if key_prefix:
                cache_key = f"{key_prefix}:{cache_key}"

            # Try to get from cache
            cached_result = await service.get(cache_key)
            if cached_result is not None:
                logger.debug("cache_decorator_hit", function=func.__name__, key=cache_key)
                return cached_result

            # Execute function
            logger.debug("cache_decorator_miss", function=func.__name__, key=cache_key)
            result = await func(*args, **kwargs)

            # Cache result
            if result is not None:
                await service.set(cache_key, result, ttl=ttl)

            return result

        return wrapper
    return decorator


# Global cache service instance
_cache_service: Optional[CacheService] = None


def init_cache_service(
    redis_url: str = "redis://localhost:6379/0",
    default_ttl: int = 300,
    enabled: bool = True
) -> CacheService:
    """
    Initialize global cache service

    Args:
        redis_url: Redis connection URL
        default_ttl: Default TTL in seconds
        enabled: Whether caching is enabled

    Returns:
        CacheService instance
    """
    global _cache_service
    _cache_service = CacheService(
        redis_url=redis_url,
        default_ttl=default_ttl,
        enabled=enabled
    )
    logger.info("cache_service_initialized", redis_url=redis_url[:30] + "...", enabled=enabled)
    return _cache_service


def get_cache_service() -> Optional[CacheService]:
    """Get global cache service instance"""
    return _cache_service


async def shutdown_cache():
    """Shutdown cache service"""
    global _cache_service
    if _cache_service:
        await _cache_service.close()
        _cache_service = None
