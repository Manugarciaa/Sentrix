"""
Cache Middleware for FastAPI

Provides HTTP response caching middleware.
"""

import hashlib
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from .cache_service import get_cache


class CacheMiddleware(BaseHTTPMiddleware):
    """
    HTTP response caching middleware.

    Caches GET responses based on URL and query parameters.
    """

    def __init__(
        self,
        app,
        default_ttl: int = 300,
        cache_methods: list = None,
        exclude_paths: list = None,
        cache_status_codes: list = None
    ):
        """
        Initialize cache middleware.

        Args:
            app: FastAPI application
            default_ttl: Default TTL in seconds (5 minutes)
            cache_methods: HTTP methods to cache (default: ["GET"])
            exclude_paths: URL paths to exclude from caching
            cache_status_codes: Status codes to cache (default: [200])
        """
        super().__init__(app)
        self.default_ttl = default_ttl
        self.cache_methods = cache_methods or ["GET"]
        self.exclude_paths = exclude_paths or []
        self.cache_status_codes = cache_status_codes or [200]
        self.cache = get_cache()

    def _should_cache(self, request: Request) -> bool:
        """
        Determine if request should be cached.

        Args:
            request: FastAPI request

        Returns:
            True if should cache, False otherwise
        """
        # Check method
        if request.method not in self.cache_methods:
            return False

        # Check excluded paths
        for excluded_path in self.exclude_paths:
            if request.url.path.startswith(excluded_path):
                return False

        # Check for cache-control header
        cache_control = request.headers.get("Cache-Control", "")
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False

        return True

    def _make_cache_key(self, request: Request) -> str:
        """
        Generate cache key from request.

        Args:
            request: FastAPI request

        Returns:
            Cache key
        """
        # Include method, path, and query params
        key_parts = [
            request.method,
            request.url.path,
            str(sorted(request.query_params.items()))
        ]

        # Include relevant headers (for API versioning, etc.)
        relevant_headers = ["Accept", "Accept-Language"]
        for header in relevant_headers:
            if header in request.headers:
                key_parts.append(f"{header}:{request.headers[header]}")

        # Create hash
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f"http:response:{key_hash}"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with caching.

        Args:
            request: FastAPI request
            call_next: Next middleware/route handler

        Returns:
            Response (cached or fresh)
        """
        # Check if should cache
        if not self._should_cache(request):
            return await call_next(request)

        # Generate cache key
        cache_key = self._make_cache_key(request)

        # Try to get cached response
        cached_response = self.cache.get(cache_key)
        if cached_response is not None:
            # Add cache hit header
            return JSONResponse(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers={
                    **cached_response.get("headers", {}),
                    "X-Cache": "HIT"
                }
            )

        # Execute request
        response = await call_next(request)

        # Cache successful responses
        if response.status_code in self.cache_status_codes:
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # Parse JSON if possible
            try:
                import json
                content = json.loads(response_body.decode())

                # Prepare cached response
                cached_data = {
                    "content": content,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }

                # Cache response
                self.cache.set(cache_key, cached_data, ttl=self.default_ttl)

                # Return fresh response with cache miss header
                return JSONResponse(
                    content=content,
                    status_code=response.status_code,
                    headers={
                        **dict(response.headers),
                        "X-Cache": "MISS"
                    }
                )

            except Exception:
                # If parsing fails, return original response
                pass

        # Add cache miss header for non-cached responses
        response.headers["X-Cache"] = "SKIP"
        return response


def cache_response(
    ttl: int = 300,
    key_prefix: str = "api"
):
    """
    Decorator for caching FastAPI route responses.

    Args:
        ttl: Time to live in seconds
        key_prefix: Cache key prefix

    Example:
        @app.get("/users/{user_id}")
        @cache_response(ttl=600)
        async def get_user(user_id: str):
            return {"user_id": user_id, "name": "John"}
    """
    from functools import wraps

    def decorator(func: Callable) -> Callable:
        cache = get_cache()

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function args
            cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"

            # Try cache
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator
