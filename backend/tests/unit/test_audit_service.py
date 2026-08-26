"""
Unit tests for AuditService
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from app.services.audit_service import AuditService
from app.models.audit import AuditLogCreate, AuditAction


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB manager."""
    mongo = Mock()
    mongo.is_connected = True
    mongo.db = Mock()
    return mongo


@pytest.fixture
def audit_service(mock_mongodb):
    """Create AuditService instance with mocked MongoDB."""
    return AuditService(mock_mongodb)


@pytest.fixture
def audit_log_data():
    """Sample audit log data for testing."""
    return AuditLogCreate(
        user_id="test_user_id",
        action=AuditAction.USER_LOGIN,
        resource_type="user",
        resource_id="test_user_id"
    )


class TestAuditService:
    """Test AuditService methods."""
    
    @pytest.mark.asyncio
    async def test_create_log(self, audit_service, audit_log_data, mock_mongodb):
        """Test creating an audit log."""
        # Mock MongoDB insert
        mock_mongodb.db.audit_logs.insert_one = AsyncMock(return_value=Mock(inserted_id="test_log_id"))
        
        log = await audit_service.create_log(audit_log_data)
        
        assert log is not None
        assert log.user_id == audit_log_data.user_id
        assert log.action == audit_log_data.action
        mock_mongodb.db.audit_logs.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_logs_by_user(self, audit_service, mock_mongodb):
        """Test getting logs by user ID."""
        # Mock MongoDB find
        mock_logs = [
            {
                "id": "log1",
                "user_id": "test_user_id",
                "action": AuditAction.USER_LOGIN,
                "resource_type": "user",
                "resource_id": "test_user_id",
                "timestamp": datetime.utcnow(),
                "ip_address": "127.0.0.1",
                "user_agent": "test"
            }
        ]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_logs)
        mock_mongodb.db.audit_logs.find.return_value.sort.return_value = mock_cursor
        
        logs = await audit_service.get_logs_by_user("test_user_id")
        
        assert len(logs) == 1
        assert logs[0].user_id == "test_user_id"
        mock_mongodb.db.audit_logs.find.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_logs_by_action(self, audit_service, mock_mongodb):
        """Test getting logs by action type."""
        # Mock MongoDB find
        mock_logs = [
            {
                "id": "log1",
                "user_id": "test_user_id",
                "action": AuditAction.USER_LOGIN,
                "resource_type": "user",
                "resource_id": "test_user_id",
                "timestamp": datetime.utcnow(),
                "ip_address": "127.0.0.1",
                "user_agent": "test"
            }
        ]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_logs)
        mock_mongodb.db.audit_logs.find.return_value.sort.return_value = mock_cursor
        
        logs = await audit_service.get_logs_by_action(AuditAction.USER_LOGIN)
        
        assert len(logs) == 1
        assert logs[0].action == AuditAction.USER_LOGIN
        mock_mongodb.db.audit_logs.find.assert_called_once()
