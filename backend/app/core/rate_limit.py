"""
Rate limiting middleware for API endpoints.
Uses slowapi for rate limiting with Redis backend.
"""

import logging
from typing import Callable
from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .redis import get_redis
from .config import get_config

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key - user ID if authenticated, otherwise IP address."""
    # Check for user ID from auth header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # In a real implementation, decode token to get user_id
        # For now, use IP address
        return get_remote_address(request)
    return get_remote_address(request)


class RateLimitMiddleware:
    """Custom rate limiting middleware."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.limiter = limiter
    
    async def __call__(self, request: Request, call_next: Callable):
        """Process request with rate limiting."""
        try:
            # Apply rate limiting
            key = get_rate_limit_key(request)
            redis_client = get_redis()
            
            # Check if rate limit exceeded
            if redis_client.is_connected:
                limit_key = f"rate_limit:{key}"
                current = await redis_client.get(limit_key)
                
                if current is None:
                    await redis_client.set(limit_key, 1, ttl=60)
                else:
                    current = int(current)
                    if current >= self.requests_per_minute:
                        logger.warning(f"Rate limit exceeded for {key}")
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Rate limit exceeded. Please try again later."
                        )
                    await redis_client.set(limit_key, current + 1, ttl=60)
            
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            if e.status_code == 429:
                raise
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting if error occurs
            response = await call_next(request)
            return response


def get_rate_limiter():
    """Get rate limiter instance."""
    config = get_config()
    return RateLimitMiddleware(requests_per_minute=config.rate_limit_per_minute)
