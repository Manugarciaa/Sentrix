"""
Rate limiting middleware for Sentrix API
Middleware de limitación de tasa para la API de Sentrix
"""

import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from typing import Callable

# Check if we're in testing mode - disable rate limiting for tests
_is_testing = os.getenv('TESTING_MODE', 'false').lower() == 'true' or os.getenv('ENVIRONMENT', '') == 'development'

# Create limiter instance (disabled in testing)
limiter = Limiter(key_func=get_remote_address, enabled=not _is_testing)


def get_limiter():
    """Get the global limiter instance"""
    return limiter


# Custom rate limit key function that uses user ID if authenticated
async def get_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key based on user authentication

    - If authenticated: use user_id
    - If not authenticated: use IP address
    """
    # Try to get user from request state (set by auth middleware)
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"

    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


def setup_rate_limiting(app):
    """
    Setup rate limiting for the FastAPI application

    Default limits:
    - General endpoints: 100 requests per minute
    - Upload endpoints: 10 requests per minute
    - Auth endpoints: 5 login attempts per minute
    """
    # Add limiter to app state
    app.state.limiter = limiter

    # Add exception handler for rate limit exceeded
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    return limiter
