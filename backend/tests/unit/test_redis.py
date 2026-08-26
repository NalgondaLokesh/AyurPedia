"""
Unit tests for RedisManager
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import timedelta

from app.core.redis import RedisManager


@pytest.fixture
def redis_manager():
    """Create RedisManager instance."""
    return RedisManager(url="redis://localhost:6379")


class TestRedisManager:
    """Test RedisManager methods."""
    
    @pytest.mark.asyncio
    async def test_connect_success(self, redis_manager):
        """Test successful Redis connection."""
        with patch('redis.asyncio.from_url') as mock_from_url:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_from_url.return_value = mock_redis
            
            result = await redis_manager.connect()
            
            assert result is True
            assert redis_manager.is_connected is True
            mock_redis.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, redis_manager):
        """Test Redis connection failure."""
        with patch('redis.asyncio.from_url') as mock_from_url:
            mock_from_url.side_effect = Exception("Connection failed")
            
            result = await redis_manager.connect()
            
            assert result is False
            assert redis_manager.is_connected is False
    
    @pytest.mark.asyncio
    async def test_get(self, redis_manager):
        """Test getting value from Redis."""
        redis_manager.is_connected = True
        redis_manager.client = AsyncMock()
        redis_manager.client.get = AsyncMock(return_value='{"test": "value"}')
        
        result = await redis_manager.get("test_key")
        
        assert result == {"test": "value"}
        redis_manager.client.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_get_not_connected(self, redis_manager):
        """Test getting value when not connected."""
        redis_manager.is_connected = False
        
        result = await redis_manager.get("test_key")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set(self, redis_manager):
        """Test setting value in Redis."""
        redis_manager.is_connected = True
        redis_manager.client = AsyncMock()
        redis_manager.client.setex = AsyncMock()
        
        result = await redis_manager.set("test_key", {"test": "value"}, ttl=3600)
        
        assert result is True
        redis_manager.client.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete(self, redis_manager):
        """Test deleting key from Redis."""
        redis_manager.is_connected = True
        redis_manager.client = AsyncMock()
        redis_manager.client.delete = AsyncMock()
        
        result = await redis_manager.delete("test_key")
        
        assert result is True
        redis_manager.client.delete.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_exists(self, redis_manager):
        """Test checking if key exists."""
        redis_manager.is_connected = True
        redis_manager.client = AsyncMock()
        redis_manager.client.exists = AsyncMock(return_value=1)
        
        result = await redis_manager.exists("test_key")
        
        assert result is True
        redis_manager.client.exists.assert_called_once_with("test_key")
