"""
Cache Decorators

Provides easy-to-use decorators for caching function results.
"""

import hashlib
import inspect
from typing import Callable, Optional, Any
from functools import wraps

from .cache_service import get_cache


def cache_key_from_args(*args, **kwargs) -> str:
    """
    Generate cache key from function arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Hash string representing the arguments
    """
    # Convert args and kwargs to a stable string representation
    key_parts = []

    for arg in args:
        if hasattr(arg, "id"):  # Handle model instances
            key_parts.append(f"{type(arg).__name__}:{arg.id}")
        else:
            key_parts.append(str(arg))

    for key, value in sorted(kwargs.items()):
        if hasattr(value, "id"):
            key_parts.append(f"{key}:{type(value).__name__}:{value.id}")
        else:
            key_parts.append(f"{key}:{value}")

    # Create hash of all parts
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(
    ttl: int = 3600,
    key_prefix: Optional[str] = None,
    serializer: str = "json",
    skip_self: bool = True
):
    """
    Cache decorator for functions and methods.

    Args:
        ttl: Time to live in seconds
        key_prefix: Custom key prefix (defaults to function name)
        serializer: Serializer to use ("json" or "pickle")
        skip_self: Skip 'self' parameter in key generation (for methods)

    Example:
        @cached(ttl=300)
        def get_user_data(user_id: str):
            # Expensive operation
            return fetch_from_database(user_id)

        # First call: executes function, caches result
        data = get_user_data("123")

        # Second call: returns cached result
        data = get_user_data("123")
    """
    def decorator(func: Callable) -> Callable:
        cache = get_cache()
        prefix = key_prefix or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_args = args[1:] if skip_self and args else args
            arg_hash = cache_key_from_args(*cache_args, **kwargs)
            cache_key = f"{prefix}:{arg_hash}"

            # Try to get from cache
            cached_value = cache.get(cache_key, serializer=serializer)
            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl, serializer=serializer)
            return result

        # Add cache control methods
        wrapper.invalidate = lambda *args, **kwargs: _invalidate_cache(
            cache, prefix, skip_self, *args, **kwargs
        )
        wrapper.clear_all = lambda: cache.delete_pattern(f"{prefix}:*")

        return wrapper

    return decorator


def _invalidate_cache(cache, prefix, skip_self, *args, **kwargs):
    """Invalidate cache for specific arguments."""
    cache_args = args[1:] if skip_self and args else args
    arg_hash = cache_key_from_args(*cache_args, **kwargs)
    cache_key = f"{prefix}:{arg_hash}"
    return cache.delete(cache_key)


def cached_property(ttl: int = 3600, key_attr: str = "id"):
    """
    Cache decorator for class properties.

    Args:
        ttl: Time to live in seconds
        key_attr: Attribute to use for cache key (defaults to "id")

    Example:
        class User:
            def __init__(self, id: str):
                self.id = id

            @cached_property(ttl=600)
            def full_profile(self):
                # Expensive operation
                return fetch_full_profile(self.id)
    """
    def decorator(func: Callable) -> property:
        cache = get_cache()

        @wraps(func)
        def wrapper(self):
            # Generate cache key from instance attribute
            instance_key = getattr(self, key_attr, id(self))
            cache_key = f"{self.__class__.__name__}.{func.__name__}:{instance_key}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute method and cache result
            result = func(self)
            cache.set(cache_key, result, ttl=ttl)
            return result

        return property(wrapper)

    return decorator


def cache_invalidate(
    pattern: Optional[str] = None,
    keys: Optional[list] = None
):
    """
    Decorator to invalidate cache after function execution.

    Args:
        pattern: Pattern to match keys for deletion
        keys: Specific keys to delete

    Example:
        @cache_invalidate(pattern="user:*")
        def update_user(user_id: str, data: dict):
            # Update user in database
            pass
    """
    def decorator(func: Callable) -> Callable:
        cache = get_cache()

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function first
            result = func(*args, **kwargs)

            # Invalidate cache
            if pattern:
                cache.delete_pattern(pattern)
            if keys:
                cache.delete_many(keys)

            return result

        return wrapper

    return decorator


def cache_aside(
    key_func: Callable,
    ttl: int = 3600,
    serializer: str = "json"
):
    """
    Cache-aside pattern decorator with custom key generation.

    Args:
        key_func: Function to generate cache key from arguments
        ttl: Time to live in seconds
        serializer: Serializer to use

    Example:
        def make_key(user_id, include_posts):
            return f"user:{user_id}:posts:{include_posts}"

        @cache_aside(key_func=make_key, ttl=300)
        def get_user_with_posts(user_id: str, include_posts: bool):
            # Fetch data
            return data
    """
    def decorator(func: Callable) -> Callable:
        cache = get_cache()

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key using custom function
            cache_key = key_func(*args, **kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key, serializer=serializer)
            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl, serializer=serializer)
            return result

        return wrapper

    return decorator


def memoize(maxsize: int = 128, ttl: int = 3600):
    """
    Memoization decorator with Redis backend.

    Similar to functools.lru_cache but using Redis for persistence
    and sharing across processes.

    Args:
        maxsize: Maximum number of cached items (not enforced in Redis)
        ttl: Time to live in seconds

    Example:
        @memoize(ttl=600)
        def fibonacci(n: int) -> int:
            if n < 2:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
    """
    return cached(ttl=ttl, serializer="pickle")


def cache_lock(
    key_func: Callable,
    timeout: int = 60,
    blocking: bool = True
):
    """
    Distributed lock decorator using Redis.

    Ensures only one process can execute the function at a time.

    Args:
        key_func: Function to generate lock key from arguments
        timeout: Lock timeout in seconds
        blocking: If True, wait for lock; if False, raise error

    Example:
        def make_lock_key(user_id):
            return f"lock:process_user:{user_id}"

        @cache_lock(key_func=make_lock_key, timeout=30)
        def process_user_data(user_id: str):
            # Critical section - only one process at a time
            pass
    """
    def decorator(func: Callable) -> Callable:
        cache = get_cache()

        @wraps(func)
        def wrapper(*args, **kwargs):
            lock_key = f"lock:{key_func(*args, **kwargs)}"

            # Try to acquire lock
            lock = cache.redis.lock(lock_key, timeout=timeout, blocking=blocking)

            try:
                if lock.acquire():
                    # Execute function with lock held
                    return func(*args, **kwargs)
                else:
                    raise RuntimeError(f"Could not acquire lock: {lock_key}")
            finally:
                try:
                    lock.release()
                except Exception:
                    pass  # Lock may have expired

        return wrapper

    return decorator
