"""
Redis Caching Layer

Provides comprehensive caching functionality with:
- Cache service for direct operations
- Decorators for easy caching
- Cache utilities for common patterns
"""

from .cache_service import (
    CacheService,
    CacheError,
    get_cache,
    reset_cache
)

from .decorators import (
    cached,
    cached_property,
    cache_invalidate,
    cache_aside,
    memoize,
    cache_lock
)

from .utils import (
    CacheStrategy,
    CacheKeyBuilder,
    cache_warm_up,
    cache_through,
    cache_stats_monitor
)


__all__ = [
    # Service
    "CacheService",
    "CacheError",
    "get_cache",
    "reset_cache",
    # Decorators
    "cached",
    "cached_property",
    "cache_invalidate",
    "cache_aside",
    "memoize",
    "cache_lock",
    # Utilities
    "CacheStrategy",
    "CacheKeyBuilder",
    "cache_warm_up",
    "cache_through",
    "cache_stats_monitor",
]
