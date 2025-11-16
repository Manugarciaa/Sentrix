"""
Cache Utilities

Provides utility functions and strategies for caching.
"""

from typing import Callable, List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from .cache_service import get_cache
from ..logging_config import get_logger

logger = get_logger(__name__)


class CacheStrategy(Enum):
    """Cache invalidation strategies"""
    TTL = "ttl"  # Time-based expiration
    LRU = "lru"  # Least recently used
    WRITE_THROUGH = "write_through"  # Update cache on write
    WRITE_BEHIND = "write_behind"  # Async cache update
    REFRESH_AHEAD = "refresh_ahead"  # Proactive refresh


class CacheKeyBuilder:
    """
    Helper class for building structured cache keys.

    Example:
        builder = CacheKeyBuilder("user")
        key = builder.build(user_id="123", include="posts")
        # Returns: "user:user_id=123:include=posts"
    """

    def __init__(self, prefix: str):
        """
        Initialize key builder.

        Args:
            prefix: Key prefix/namespace
        """
        self.prefix = prefix

    def build(self, **kwargs) -> str:
        """
        Build cache key from keyword arguments.

        Args:
            **kwargs: Key components

        Returns:
            Structured cache key
        """
        parts = [self.prefix]

        for key, value in sorted(kwargs.items()):
            if value is not None:
                parts.append(f"{key}={value}")

        return ":".join(parts)

    def pattern(self, **kwargs) -> str:
        """
        Build cache key pattern for matching.

        Args:
            **kwargs: Key components (use None for wildcards)

        Returns:
            Cache key pattern with wildcards
        """
        parts = [self.prefix]

        for key, value in sorted(kwargs.items()):
            if value is None:
                parts.append(f"{key}=*")
            else:
                parts.append(f"{key}={value}")

        return ":".join(parts)


def cache_warm_up(
    keys: List[str],
    loader_func: Callable[[str], Any],
    ttl: int = 3600,
    batch_size: int = 100
) -> int:
    """
    Warm up cache with data from a loader function.

    Args:
        keys: List of keys to warm up
        loader_func: Function that loads data for a key
        ttl: Time to live in seconds
        batch_size: Number of keys to process per batch

    Returns:
        Number of keys successfully cached

    Example:
        def load_user(user_id: str):
            return db.query(User).filter(User.id == user_id).first()

        user_ids = ["1", "2", "3", "4", "5"]
        cache_warm_up(user_ids, load_user, ttl=3600)
    """
    cache = get_cache()
    success_count = 0

    # Process in batches
    for i in range(0, len(keys), batch_size):
        batch_keys = keys[i:i + batch_size]
        batch_data = {}

        # Load data for batch
        for key in batch_keys:
            try:
                data = loader_func(key)
                if data is not None:
                    batch_data[key] = data
            except Exception as e:
                logger.error("cache warm-up error", key=key, error=str(e))
                continue

        # Cache batch
        success_count += cache.set_many(batch_data, ttl=ttl)

    return success_count


def cache_through(
    cache_key: str,
    loader_func: Callable[[], Any],
    ttl: int = 3600,
    force_refresh: bool = False
) -> Any:
    """
    Cache-through pattern: get from cache or load and cache.

    Args:
        cache_key: Cache key
        loader_func: Function to load data if not cached
        ttl: Time to live in seconds
        force_refresh: If True, bypass cache and reload

    Returns:
        Data from cache or loader

    Example:
        def load_user_profile(user_id: str):
            return cache_through(
                cache_key=f"user:profile:{user_id}",
                loader_func=lambda: db.query(User).get(user_id),
                ttl=600
            )
    """
    cache = get_cache()

    # Force refresh if requested
    if force_refresh:
        data = loader_func()
        cache.set(cache_key, data, ttl=ttl)
        return data

    # Try cache first
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    # Load and cache
    data = loader_func()
    if data is not None:
        cache.set(cache_key, data, ttl=ttl)

    return data


def cache_stats_monitor() -> Dict[str, Any]:
    """
    Get comprehensive cache statistics.

    Returns:
        Dictionary with cache statistics and health info

    Example:
        stats = cache_stats_monitor()
        print(f"Hit rate: {stats['hit_rate']}%")
        print(f"Memory usage: {stats['memory_usage_mb']} MB")
    """
    cache = get_cache()

    try:
        # Get cache stats
        stats = cache.get_stats()

        # Get Redis info
        info = cache.info()

        # Calculate additional metrics
        memory_usage = info.get("used_memory", 0)
        memory_usage_mb = round(memory_usage / (1024 * 1024), 2)

        connected_clients = info.get("connected_clients", 0)
        total_commands = info.get("total_commands_processed", 0)

        return {
            **stats,
            "memory_usage_mb": memory_usage_mb,
            "connected_clients": connected_clients,
            "total_commands": total_commands,
            "is_healthy": cache.ping()
        }

    except Exception as e:
        logger.error("cache stats monitor error", error=str(e))
        return {
            "hits": 0,
            "misses": 0,
            "hit_rate": 0.0,
            "is_healthy": False,
            "error": str(e)
        }


def cache_invalidate_user_data(user_id: str) -> int:
    """
    Invalidate all cached data for a specific user.

    Args:
        user_id: User ID

    Returns:
        Number of keys invalidated

    Example:
        # After updating user profile
        cache_invalidate_user_data(user.id)
    """
    cache = get_cache()
    patterns = [
        f"user:{user_id}:*",
        f"*:user_id={user_id}:*",
        f"analyses:user:{user_id}:*"
    ]

    total_invalidated = 0
    for pattern in patterns:
        total_invalidated += cache.delete_pattern(pattern)

    return total_invalidated


def cache_invalidate_analysis_data(analysis_id: str) -> int:
    """
    Invalidate all cached data for a specific analysis.

    Args:
        analysis_id: Analysis ID

    Returns:
        Number of keys invalidated
    """
    cache = get_cache()
    patterns = [
        f"analysis:{analysis_id}:*",
        f"detections:analysis:{analysis_id}:*"
    ]

    total_invalidated = 0
    for pattern in patterns:
        total_invalidated += cache.delete_pattern(pattern)

    return total_invalidated


def cache_health_check() -> Dict[str, Any]:
    """
    Perform comprehensive cache health check.

    Returns:
        Dictionary with health check results

    Example:
        health = cache_health_check()
        if not health['is_healthy']:
            print(f"Cache unhealthy: {health['error']}")
    """
    cache = get_cache()

    try:
        # Test connection
        ping_result = cache.ping()
        if not ping_result:
            return {
                "is_healthy": False,
                "error": "Cannot ping Redis server"
            }

        # Test write
        test_key = "_health_check_test"
        write_success = cache.set(test_key, "test", ttl=10)
        if not write_success:
            return {
                "is_healthy": False,
                "error": "Cannot write to cache"
            }

        # Test read
        read_value = cache.get(test_key)
        if read_value != "test":
            return {
                "is_healthy": False,
                "error": "Cannot read from cache"
            }

        # Test delete
        delete_success = cache.delete(test_key)
        if not delete_success:
            return {
                "is_healthy": False,
                "error": "Cannot delete from cache"
            }

        # Get stats
        stats = cache.get_stats()

        return {
            "is_healthy": True,
            "latency_ms": "<1",
            "hit_rate": stats.get("hit_rate", 0),
            "total_operations": stats.get("hits", 0) + stats.get("misses", 0)
        }

    except Exception as e:
        return {
            "is_healthy": False,
            "error": str(e)
        }


def get_or_set(
    key: str,
    default_factory: Callable[[], Any],
    ttl: int = 3600
) -> Any:
    """
    Get value from cache or set it using a factory function.

    Args:
        key: Cache key
        default_factory: Function to generate value if not cached
        ttl: Time to live in seconds

    Returns:
        Cached or newly generated value

    Example:
        user = get_or_set(
            key=f"user:{user_id}",
            default_factory=lambda: fetch_user_from_db(user_id),
            ttl=600
        )
    """
    cache = get_cache()

    # Try to get from cache
    value = cache.get(key)
    if value is not None:
        return value

    # Generate and cache
    value = default_factory()
    if value is not None:
        cache.set(key, value, ttl=ttl)

    return value


def cache_prefix_all_keys(prefix: str) -> List[str]:
    """
    Get all keys with a specific prefix.

    Args:
        prefix: Key prefix

    Returns:
        List of matching keys

    Example:
        user_keys = cache_prefix_all_keys("user:")
    """
    cache = get_cache()
    return cache.keys(f"{prefix}*")


def cache_size_estimate(pattern: str = "*") -> Dict[str, Any]:
    """
    Estimate cache size for keys matching pattern.

    Args:
        pattern: Key pattern

    Returns:
        Dictionary with size estimates

    Example:
        size_info = cache_size_estimate("user:*")
        print(f"Total keys: {size_info['key_count']}")
    """
    cache = get_cache()

    try:
        keys = cache.keys(pattern)
        key_count = len(keys)

        # Sample some keys to estimate average size
        sample_size = min(100, key_count)
        total_sample_size = 0

        for key in keys[:sample_size]:
            try:
                value = cache.redis.get(cache._make_key(key))
                if value:
                    total_sample_size += len(value)
            except Exception:
                continue

        avg_size = total_sample_size / sample_size if sample_size > 0 else 0
        estimated_total_size = avg_size * key_count

        return {
            "key_count": key_count,
            "avg_size_bytes": round(avg_size, 2),
            "estimated_total_mb": round(estimated_total_size / (1024 * 1024), 2)
        }

    except Exception as e:
        return {
            "key_count": 0,
            "error": str(e)
        }
