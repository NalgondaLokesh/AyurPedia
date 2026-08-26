"""
Unit tests for AuthService
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

from app.services.auth_service import AuthService
from app.models.user import UserCreate, UserResponse
from app.core.auth import hash_password, verify_password


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB manager."""
    mongo = Mock()
    mongo.is_connected = True
    mongo.db = Mock()
    return mongo


@pytest.fixture
def auth_service(mock_mongodb):
    """Create AuthService instance with mocked MongoDB."""
    return AuthService(mock_mongodb)


@pytest.fixture
def user_data():
    """Sample user data for testing."""
    return UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        full_name="Test User",
        organization="Test Org"
    )


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 50  # bcrypt hashes are long
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestAuthService:
    """Test AuthService methods."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, auth_service, user_data, mock_mongodb):
        """Test user creation."""
        # Mock MongoDB insert
        mock_mongodb.db.users.insert_one = AsyncMock(return_value=Mock(inserted_id="test_id"))
        
        user = await auth_service.create_user(user_data)
        
        assert user.email == user_data.email
        assert user.full_name == user_data.full_name
        assert user.id == "test_id"
        assert user.hashed_password != user_data.password  # Password should be hashed
        mock_mongodb.db.users.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, auth_service, user_data, mock_mongodb):
        """Test getting user by email."""
        # Mock MongoDB find
        mock_user_doc = {
            "id": "test_id",
            "email": user_data.email,
            "full_name": user_data.full_name,
            "organization": user_data.organization,
            "hashed_password": hash_password(user_data.password),
            "created_at": datetime.utcnow(),
            "consent_given": False,
            "privacy_settings": {}
        }
        mock_mongodb.db.users.find_one = AsyncMock(return_value=mock_user_doc)
        
        user = await auth_service.get_user_by_email(user_data.email)
        
        assert user is not None
        assert user.email == user_data.email
        mock_mongodb.db.users.find_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, user_data, mock_mongodb):
        """Test successful user authentication."""
        # Mock user document
        mock_user_doc = {
            "id": "test_id",
            "email": user_data.email,
            "full_name": user_data.full_name,
            "organization": user_data.organization,
            "hashed_password": hash_password(user_data.password),
            "created_at": datetime.utcnow(),
            "consent_given": False,
            "privacy_settings": {}
        }
        mock_mongodb.db.users.find_one = AsyncMock(return_value=mock_user_doc)
        
        user = await auth_service.authenticate_user(user_data.email, user_data.password)
        
        assert user is not None
        assert user.email == user_data.email
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, auth_service, user_data, mock_mongodb):
        """Test authentication with wrong password."""
        mock_user_doc = {
            "id": "test_id",
            "email": user_data.email,
            "full_name": user_data.full_name,
            "organization": user_data.organization,
            "hashed_password": hash_password(user_data.password),
            "created_at": datetime.utcnow(),
            "consent_given": False,
            "privacy_settings": {}
        }
        mock_mongodb.db.users.find_one = AsyncMock(return_value=mock_user_doc)
        
        user = await auth_service.authenticate_user(user_data.email, "WrongPassword123!")
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_delete_user(self, auth_service, user_data, mock_mongodb):
        """Test user deletion."""
        mock_mongodb.db.users.delete_one = AsyncMock(return_value=Mock(deleted_count=1))
        
        result = await auth_service.delete_user("test_id")
        
        assert result is True
        mock_mongodb.db.users.delete_one.assert_called_once()
