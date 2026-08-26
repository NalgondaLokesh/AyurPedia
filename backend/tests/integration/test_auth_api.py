"""
Integration tests for Authentication API endpoints
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from main import app
from app.core.mongodb import get_mongodb
from app.services.audit_service import get_audit_service


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
    mongo.db.audit_logs = Mock()
    return mongo


@pytest.fixture
def mock_audit_service():
    """Mock audit service."""
    service = Mock()
    service.create_log = AsyncMock()
    return service


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


class TestAuthAPI:
    """Test authentication API endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_user(self, client, mock_mongodb):
        """Test user registration endpoint."""
        mock_mongodb.db.users.find_one = AsyncMock(return_value=None)
        mock_mongodb.db.users.insert_one = AsyncMock(return_value=Mock(inserted_id="test_id"))
        
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
                "full_name": "Test User",
                "organization": "Test Org"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, mock_mongodb):
        """Test registration with duplicate email."""
        mock_mongodb.db.users.find_one = AsyncMock(return_value={"email": "test@example.com"})
        
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_login_success(self, client, mock_mongodb):
        """Test successful login."""
        from app.core.auth import hash_password
        
        mock_user = {
            "id": "test_id",
            "email": "test@example.com",
            "full_name": "Test User",
            "organization": "Test Org",
            "hashed_password": hash_password("TestPassword123!"),
            "created_at": datetime.utcnow(),
            "consent_given": False,
            "privacy_settings": {}
        }
        mock_mongodb.db.users.find_one = AsyncMock(return_value=mock_user)
        
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "TestPassword123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, mock_mongodb):
        """Test login with wrong password."""
        from app.core.auth import hash_password
        
        mock_user = {
            "id": "test_id",
            "email": "test@example.com",
            "full_name": "Test User",
            "hashed_password": hash_password("CorrectPassword123!"),
            "created_at": datetime.utcnow(),
            "consent_given": False,
            "privacy_settings": {}
        }
        mock_mongodb.db.users.find_one = AsyncMock(return_value=mock_user)
        
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client, mock_mongodb):
        """Test getting current user with valid token."""
        from app.core.auth import create_access_token
        
        mock_user = {
            "id": "test_id",
            "email": "test@example.com",
            "full_name": "Test User",
            "organization": "Test Org",
            "hashed_password": "hashed",
            "created_at": datetime.utcnow(),
            "consent_given": False,
            "privacy_settings": {}
        }
        mock_mongodb.db.users.find_one = AsyncMock(return_value=mock_user)
        
        token = create_access_token(data={"sub": "test_id"})
        
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
