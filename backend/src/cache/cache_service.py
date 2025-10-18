"""
Redis Cache Service

Provides caching functionality using Redis with:
- Multiple cache strategies (LRU, TTL-based)
- Automatic serialization/deserialization
- Cache key generation
- Cache invalidation patterns
- Performance monitoring
"""

import json
import pickle
import hashlib
from typing import Optional, Any, Callable, Union, List
from datetime import timedelta
from functools import wraps

import redis
from redis.exceptions import RedisError

from ..config import get_settings
from ..logging_config import get_logger

logger = get_logger(__name__)


class CacheError(Exception):
    """Base exception for cache errors"""
    pass


class CacheService:
    """
    Redis-based caching service with automatic serialization.

    Supports:
    - TTL-based expiration
    - JSON and pickle serialization
    - Namespace isolation
    - Batch operations
    - Cache statistics
    """

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        namespace: str = "sentrix",
        default_ttl: int = 3600
    ):
        """
        Initialize cache service.

        Args:
            redis_client: Redis client instance (creates one if None)
            namespace: Cache key namespace/prefix
            default_ttl: Default TTL in seconds (1 hour)
        """
        if redis_client is None:
            settings = get_settings()
            self.redis = redis.from_url(
                settings.redis_url,
                decode_responses=False  # Handle binary data
            )
        else:
            self.redis = redis_client

        self.namespace = namespace
        self.default_ttl = default_ttl
        self._stats_key = f"{namespace}:cache_stats"

    # ============================================
    # Core Operations
    # ============================================

    def _make_key(self, key: str) -> str:
        """
        Generate namespaced cache key.

        Args:
            key: Base key

        Returns:
            Namespaced key
        """
        return f"{self.namespace}:{key}"

    def get(
        self,
        key: str,
        default: Any = None,
        deserializer: str = "json"
    ) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found
            deserializer: Deserializer to use ("json" or "pickle")

        Returns:
            Cached value or default
        """
        try:
            cache_key = self._make_key(key)
            value = self.redis.get(cache_key)

            if value is None:
                self._increment_stat("misses")
                return default

            self._increment_stat("hits")

            # Deserialize
            if deserializer == "json":
                return json.loads(value)
            elif deserializer == "pickle":
                return pickle.loads(value)
            else:
                return value

        except RedisError as e:
            # Log error but don't fail the application
            logger.error("cache get error", key=key, error=str(e))
            return default
        except Exception as e:
            logger.error("cache deserialization error", key=key, error=str(e))
            return default

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serializer: str = "json"
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = use default)
            serializer: Serializer to use ("json" or "pickle")

        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = self._make_key(key)
            ttl = ttl or self.default_ttl

            # Serialize
            if serializer == "json":
                serialized = json.dumps(value)
            elif serializer == "pickle":
                serialized = pickle.dumps(value)
            else:
                serialized = value

            # Set with TTL
            self.redis.setex(cache_key, ttl, serialized)
            self._increment_stat("sets")
            return True

        except RedisError as e:
            logger.error("cache set error", key=key, error=str(e))
            return False
        except Exception as e:
            logger.error("cache serialization error", key=key, error=str(e))
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        try:
            cache_key = self._make_key(key)
            result = self.redis.delete(cache_key)
            if result:
                self._increment_stat("deletes")
            return bool(result)
        except RedisError as e:
            logger.error("cache delete error", key=key, error=str(e))
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        try:
            cache_key = self._make_key(key)
            return bool(self.redis.exists(cache_key))
        except RedisError as e:
            logger.error("cache exists error", key=key, error=str(e))
            return False

    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for a key.

        Args:
            key: Cache key

        Returns:
            Remaining TTL in seconds, None if key doesn't exist or no TTL
        """
        try:
            cache_key = self._make_key(key)
            ttl = self.redis.ttl(cache_key)
            return ttl if ttl > 0 else None
        except RedisError as e:
            logger.error("cache ttl error", key=key, error=str(e))
            return None

    def expire(self, key: str, ttl: int) -> bool:
        """
        Set/update TTL for a key.

        Args:
            key: Cache key
            ttl: New TTL in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = self._make_key(key)
            return bool(self.redis.expire(cache_key, ttl))
        except RedisError as e:
            logger.error("cache expire error", key=key, error=str(e))
            return False

    # ============================================
    # Batch Operations
    # ============================================

    def get_many(
        self,
        keys: List[str],
        deserializer: str = "json"
    ) -> dict:
        """
        Get multiple values from cache.

        Args:
            keys: List of cache keys
            deserializer: Deserializer to use

        Returns:
            Dictionary of key-value pairs (only existing keys)
        """
        try:
            cache_keys = [self._make_key(k) for k in keys]
            values = self.redis.mget(cache_keys)

            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        if deserializer == "json":
                            result[key] = json.loads(value)
                        elif deserializer == "pickle":
                            result[key] = pickle.loads(value)
                        else:
                            result[key] = value
                    except Exception:
                        continue

            self._increment_stat("hits", len(result))
            self._increment_stat("misses", len(keys) - len(result))
            return result

        except RedisError as e:
            logger.error("cache get_many error", keys_count=len(keys), error=str(e))
            return {}

    def set_many(
        self,
        mapping: dict,
        ttl: Optional[int] = None,
        serializer: str = "json"
    ) -> int:
        """
        Set multiple values in cache.

        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time to live in seconds
            serializer: Serializer to use

        Returns:
            Number of keys successfully set
        """
        try:
            ttl = ttl or self.default_ttl
            pipe = self.redis.pipeline()

            for key, value in mapping.items():
                cache_key = self._make_key(key)
                try:
                    if serializer == "json":
                        serialized = json.dumps(value)
                    elif serializer == "pickle":
                        serialized = pickle.dumps(value)
                    else:
                        serialized = value

                    pipe.setex(cache_key, ttl, serialized)
                except Exception:
                    continue

            results = pipe.execute()
            success_count = sum(1 for r in results if r)
            self._increment_stat("sets", success_count)
            return success_count

        except RedisError as e:
            logger.error("cache set_many error", keys_count=len(mapping), error=str(e))
            return 0

    def delete_many(self, keys: List[str]) -> int:
        """
        Delete multiple keys from cache.

        Args:
            keys: List of cache keys

        Returns:
            Number of keys deleted
        """
        try:
            cache_keys = [self._make_key(k) for k in keys]
            count = self.redis.delete(*cache_keys)
            self._increment_stat("deletes", count)
            return count
        except RedisError as e:
            logger.error("cache delete_many error", keys_count=len(keys), error=str(e))
            return 0

    # ============================================
    # Pattern Operations
    # ============================================

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Key pattern (supports * wildcard)

        Returns:
            Number of keys deleted
        """
        try:
            cache_pattern = self._make_key(pattern)
            keys = list(self.redis.scan_iter(match=cache_pattern))

            if keys:
                count = self.redis.delete(*keys)
                self._increment_stat("deletes", count)
                return count
            return 0

        except RedisError as e:
            logger.error("cache delete_pattern error", pattern=pattern, error=str(e))
            return 0

    def keys(self, pattern: str = "*") -> List[str]:
        """
        Get all keys matching a pattern.

        Args:
            pattern: Key pattern (supports * wildcard)

        Returns:
            List of matching keys (without namespace prefix)
        """
        try:
            cache_pattern = self._make_key(pattern)
            keys = list(self.redis.scan_iter(match=cache_pattern))

            # Remove namespace prefix
            prefix_len = len(self.namespace) + 1
            return [k.decode() if isinstance(k, bytes) else k[prefix_len:] for k in keys]

        except RedisError as e:
            logger.error("cache keys error", pattern=pattern, error=str(e))
            return []

    # ============================================
    # Cache Management
    # ============================================

    def clear(self) -> int:
        """
        Clear all keys in this namespace.

        Returns:
            Number of keys deleted
        """
        return self.delete_pattern("*")

    def clear_all(self) -> bool:
        """
        Clear entire Redis database (use with caution!).

        Returns:
            True if successful, False otherwise
        """
        try:
            self.redis.flushdb()
            return True
        except RedisError as e:
            logger.error("cache clear_all error", error=str(e))
            return False

    # ============================================
    # Statistics
    # ============================================

    def _increment_stat(self, stat_name: str, count: int = 1) -> None:
        """Increment cache statistics counter."""
        try:
            self.redis.hincrby(self._stats_key, stat_name, count)
        except RedisError:
            pass  # Don't fail on stats errors

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            stats = self.redis.hgetall(self._stats_key)

            # Decode bytes keys/values
            decoded_stats = {}
            for key, value in stats.items():
                key_str = key.decode() if isinstance(key, bytes) else key
                val_int = int(value.decode() if isinstance(value, bytes) else value)
                decoded_stats[key_str] = val_int

            # Calculate hit rate
            hits = decoded_stats.get("hits", 0)
            misses = decoded_stats.get("misses", 0)
            total = hits + misses

            if total > 0:
                decoded_stats["hit_rate"] = round(hits / total * 100, 2)
            else:
                decoded_stats["hit_rate"] = 0.0

            return decoded_stats

        except RedisError as e:
            logger.error("cache stats error", error=str(e))
            return {"hits": 0, "misses": 0, "sets": 0, "deletes": 0, "hit_rate": 0.0}

    def reset_stats(self) -> bool:
        """
        Reset cache statistics.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.redis.delete(self._stats_key)
            return True
        except RedisError as e:
            logger.error("cache reset_stats error", error=str(e))
            return False

    # ============================================
    # Health Check
    # ============================================

    def ping(self) -> bool:
        """
        Check if Redis connection is alive.

        Returns:
            True if connected, False otherwise
        """
        try:
            return self.redis.ping()
        except RedisError:
            return False

    def info(self) -> dict:
        """
        Get Redis server information.

        Returns:
            Dictionary with server info
        """
        try:
            return self.redis.info()
        except RedisError as e:
            logger.error("cache info error", error=str(e))
            return {}


# ============================================
# Global Cache Instance
# ============================================

_cache_service: Optional[CacheService] = None


def get_cache() -> CacheService:
    """
    Get global cache service instance.

    Returns:
        CacheService instance
    """
    global _cache_service

    if _cache_service is None:
        _cache_service = CacheService()

    return _cache_service


def reset_cache() -> None:
    """Reset global cache instance (useful for testing)."""
    global _cache_service
    _cache_service = None
