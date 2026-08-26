"""
Integration tests for Conversations API endpoints
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from main import app
from app.core.mongodb import get_mongodb
from app.services.audit_service import get_audit_service
from app.core.auth import create_access_token


@pytest.fixture
async def client():
    """Create async test client."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB for testing."""
    mongo = Mock()
    mongo.is_connected = True
    mongo.db = Mock()
    mongo.db.users = Mock()
    mongo.db.conversations = Mock()
    mongo.db.audit_logs = Mock()
    return mongo


@pytest.fixture
def mock_audit_service():
    """Mock audit service."""
    service = Mock()
    service.create_log = AsyncMock()
    return service


@pytest.fixture
def auth_token():
    """Create valid auth token."""
    return create_access_token(data={"sub": "test_user_id"})


@pytest.fixture(autouse=True)
def override_dependencies(mock_mongodb, mock_audit_service):
    """Override dependencies for testing."""
    def get_test_mongodb():
        return mock_mongodb
    
    def get_test_audit_service():
        return mock_audit_service
    
    app.dependency_overrides[get_mongodb] = get_test_mongodb
    app.dependency_overrides[get_audit_service] = get_test_audit_service
    
    yield
    
    app.dependency_overrides.clear()


class TestConversationsAPI:
    """Test conversations API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, client, mock_mongodb, auth_token):
        """Test creating a new conversation."""
        mock_mongodb.db.conversations.insert_one = AsyncMock(return_value=Mock(inserted_id="test_id"))
        
        response = await client.post(
            "/api/conversations",
            json={
                "title": "Test Conversation",
                "jurisdiction": "India",
                "language": "en"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Conversation"
        assert data["jurisdiction"] == "India"
    
    @pytest.mark.asyncio
    async def test_list_conversations(self, client, mock_mongodb, auth_token):
        """Test listing conversations."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {
                "conversation_id": "conv1",
                "user_id": "test_user_id",
                "title": "Test Conversation",
                "jurisdiction": "India",
                "language": "en",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "messages": []
            }
        ])
        mock_mongodb.db.conversations.find.return_value.sort.return_value = mock_cursor
        
        response = await client.get(
            "/api/conversations",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Conversation"
    
    @pytest.mark.asyncio
    async def test_get_conversation(self, client, mock_mongodb, auth_token):
        """Test getting a specific conversation."""
        mock_mongodb.db.conversations.find_one = AsyncMock(return_value={
            "conversation_id": "conv1",
            "user_id": "test_user_id",
            "title": "Test Conversation",
            "jurisdiction": "India",
            "language": "en",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": []
        })
        
        response = await client.get(
            "/api/conversations/conv1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == "conv1"
    
    @pytest.mark.asyncio
    async def test_add_message(self, client, mock_mongodb, auth_token):
        """Test adding a message to a conversation."""
        mock_mongodb.db.conversations.find_one = AsyncMock(return_value={
            "conversation_id": "conv1",
            "user_id": "test_user_id",
            "title": "Test Conversation",
            "jurisdiction": "India",
            "language": "en",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": []
        })
        mock_mongodb.db.conversations.update_one = AsyncMock()
        
        response = await client.post(
            "/api/conversations/conv1/messages",
            json={
                "sender": "user",
                "text": "Test message",
                "citations": [],
                "confidence": 0.9
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_delete_conversation(self, client, mock_mongodb, auth_token):
        """Test deleting a conversation."""
        mock_mongodb.db.conversations.delete_one = AsyncMock(return_value=Mock(deleted_count=1))
        
        response = await client.delete(
            "/api/conversations/conv1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Conversation deleted successfully"
