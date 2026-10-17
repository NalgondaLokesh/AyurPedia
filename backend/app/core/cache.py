"""
Simple in-memory cache for reducing API calls and latency.
"""

import hashlib
import json
import logging
from typing import Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL."""

    def __init__(self, ttl_minutes: int = 60):
        """Initialize cache with time-to-live.

        Args:
            ttl_minutes: Time-to-live in minutes for cache entries
        """
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        logger.info(f"Cache initialized with TTL: {ttl_minutes} minutes")

    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Hash string as cache key
        """
        # Create a deterministic string representation
        key_parts = []
        for arg in args:
            key_parts.append(str(arg))
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")

        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, *args, **kwargs) -> Optional[Any]:
        """Get value from cache if exists and not expired.

        Args:
            *args: Cache key arguments
            **kwargs: Cache key keyword arguments

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        key = self._generate_key(*args, **kwargs)

        if key in self.cache:
            entry = self.cache[key]
            # Check if expired
            if datetime.now() - entry['timestamp'] < self.ttl:
                logger.debug(f"Cache hit for key: {key[:8]}...")
                return entry['value']
            else:
                # Remove expired entry
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key[:8]}...")

        return None

    def set(self, value: Any, *args, **kwargs) -> None:
        """Set value in cache.

        Args:
            value: Value to cache
            *args: Cache key arguments
            **kwargs: Cache key keyword arguments
        """
        key = self._generate_key(*args, **kwargs)
        self.cache[key] = {
            'value': value,
            'timestamp': datetime.now()
        }
        logger.debug(f"Cache set for key: {key[:8]}...")

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")

    def size(self) -> int:
        """Get current cache size.

        Returns:
            Number of entries in cache
        """
        return len(self.cache)


# Global cache instance
_retrieval_cache = None
_embedding_cache = None


def get_retrieval_cache() -> SimpleCache:
    """Get or create global retrieval cache."""
    global _retrieval_cache
    if _retrieval_cache is None:
        _retrieval_cache = SimpleCache(ttl_minutes=30)  # 30 minutes for retrieval
    return _retrieval_cache


def get_embedding_cache() -> SimpleCache:
    """Get or create global embedding cache."""
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = SimpleCache(ttl_minutes=120)  # 2 hours for embeddings
    return _embedding_cache
