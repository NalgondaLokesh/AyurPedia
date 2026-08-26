"""
Redis caching manager for AyurPedia.
Provides caching for frequent queries and responses.
"""

import logging
import json
from typing import Optional, Any
from datetime import timedelta
import redis.asyncio as redis

from .config import get_config

logger = logging.getLogger(__name__)


class RedisManager:
    """Manager for Redis caching operations."""
    
    def __init__(self, url: str = None):
        self.url = url or get_config().redis_url
        self.client: Optional[redis.Redis] = None
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Initialize Redis connection."""
        try:
            self.client = redis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.client.ping()
            self.is_connected = True
            logger.info(f"Connected to Redis: {self.url}")
            return True
        except Exception as e:
            logger.warning(f"Redis connection failed ({e}). Running without caching.")
            self.is_connected = False
            return False
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            self.is_connected = False
            logger.info("Redis connection closed.")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.is_connected or not self.client:
            return None
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL in seconds."""
        if not self.is_connected or not self.client:
            return False
        try:
            await self.client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.is_connected or not self.client:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        if not self.is_connected or not self.client:
            return 0
        try:
            keys = await self.client.keys(pattern)
            if keys:
                await self.client.delete(*keys)
            return len(keys)
        except Exception as e:
            logger.error(f"Redis delete_pattern error: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.is_connected or not self.client:
            return False
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False


# Global Redis manager instance
_redis_manager: Optional[RedisManager] = None


def get_redis() -> RedisManager:
    """Get or initialize global Redis manager."""
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisManager()
    return _redis_manager
