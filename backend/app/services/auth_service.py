"""
Authentication service for user management.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from ..core.mongodb import get_mongodb
from ..core.auth import verify_password, get_password_hash, create_access_token, create_refresh_token
from ..models.user import UserCreate, UserInDB, UserResponse, ConsentUpdate, PrivacySettings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication and user management."""
    
    def __init__(self):
        self.mongodb = get_mongodb()
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        mongodb = get_mongodb()
        
        # Check if user already exists
        if mongodb.is_connected and mongodb.db is not None:
            existing_user = await mongodb.db.users.find_one({"email": user_data.email})
            if existing_user:
                raise ValueError("User with this email already exists")
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "full_name": user_data.full_name,
            "organization": user_data.organization,
            "hashed_password": get_password_hash(user_data.password),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "consent_given": False,
            "privacy_settings": {
                "data_retention_days": 90,
                "allow_analytics": False,
                "allow_marketing": False,
                "conversation_history_enabled": True
            }
        }
        
        if mongodb.is_connected and mongodb.db is not None:
            result = await mongodb.db.users.insert_one(user_doc)
            user_doc["id"] = str(result.inserted_id)
        else:
            user_doc["id"] = "mem_" + str(len(mongodb._memory_store.get("users", [])))
            if "users" not in mongodb._memory_store:
                mongodb._memory_store["users"] = []
            mongodb._memory_store["users"].append(user_doc)
        
        return UserResponse(
            id=user_doc["id"],
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            organization=user_doc["organization"],
            is_active=user_doc["is_active"],
            created_at=user_doc["created_at"],
            consent_given=user_doc["consent_given"]
        )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate a user with email and password."""
        mongodb = get_mongodb()
        user_doc = None
        
        if mongodb.is_connected and mongodb.db is not None:
            user_doc = await mongodb.db.users.find_one({"email": email})
        else:
            for user in mongodb._memory_store.get("users", []):
                if user["email"] == email:
                    user_doc = user
                    break
        
        if not user_doc:
            return None
        
        if not verify_password(password, user_doc["hashed_password"]):
            return None
        
        # Handle both MongoDB _id and custom id field
        user_id = str(user_doc.get("_id")) if user_doc.get("_id") else user_doc.get("id")
        if not user_id:
            logger.error(f"User document missing both _id and id: {user_doc}")
            return None

        return UserInDB(
            id=user_id,
            email=user_doc["email"],
            full_name=user_doc.get("full_name"),
            organization=user_doc.get("organization"),
            hashed_password=user_doc["hashed_password"],
            is_active=user_doc.get("is_active", True),
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"],
            consent_given=user_doc.get("consent_given", False),
            privacy_settings=user_doc.get("privacy_settings", {})
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID."""
        mongodb = get_mongodb()
        user_doc = None
        
        if mongodb.is_connected and mongodb.db is not None:
            try:
                user_doc = await mongodb.db.users.find_one({"_id": ObjectId(user_id)})
            except:
                user_doc = await mongodb.db.users.find_one({"id": user_id})
        else:
            for user in mongodb._memory_store.get("users", []):
                if user["id"] == user_id:
                    user_doc = user
                    break
        
        if not user_doc:
            return None
        
        # Handle both MongoDB _id and custom id field
        user_id = str(user_doc.get("_id")) if user_doc.get("_id") else user_doc.get("id")
        if not user_id:
            logger.error(f"User document missing both _id and id: {user_doc}")
            return None

        return UserInDB(
            id=user_id,
            email=user_doc["email"],
            full_name=user_doc.get("full_name"),
            organization=user_doc.get("organization"),
            hashed_password=user_doc["hashed_password"],
            is_active=user_doc.get("is_active", True),
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"],
            consent_given=user_doc.get("consent_given", False),
            privacy_settings=user_doc.get("privacy_settings", {})
        )
    
    async def update_consent(self, user_id: str, consent_data: ConsentUpdate) -> bool:
        """Update user consent."""
        mongodb = get_mongodb()
        update_data = {
            "consent_given": consent_data.consent_given,
            "updated_at": datetime.utcnow()
        }
        if consent_data.consent_date:
            update_data["consent_date"] = consent_data.consent_date
        
        if mongodb.is_connected and mongodb.db is not None:
            try:
                result = await mongodb.db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_data}
                )
                return result.modified_count > 0
            except:
                result = await mongodb.db.users.update_one(
                    {"id": user_id},
                    {"$set": update_data}
                )
                return result.modified_count > 0
        else:
            for user in mongodb._memory_store.get("users", []):
                if user["id"] == user_id:
                    user.update(update_data)
                    return True
        return False
    
    async def update_privacy_settings(self, user_id: str, settings: PrivacySettings) -> bool:
        """Update user privacy settings."""
        mongodb = get_mongodb()
        update_data = {
            "privacy_settings": settings.dict(),
            "updated_at": datetime.utcnow()
        }
        
        if mongodb.is_connected and mongodb.db is not None:
            try:
                result = await mongodb.db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_data}
                )
                return result.modified_count > 0
            except:
                result = await mongodb.db.users.update_one(
                    {"id": user_id},
                    {"$set": update_data}
                )
                return result.modified_count > 0
        else:
            for user in mongodb._memory_store.get("users", []):
                if user["id"] == user_id:
                    user.update(update_data)
                    return True
        return False
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user and all associated data."""
        mongodb = get_mongodb()
        
        if mongodb.is_connected and mongodb.db is not None:
            try:
                # Delete user
                await mongodb.db.users.delete_one({"_id": ObjectId(user_id)})
                # Delete user's conversations
                await mongodb.db.conversations.delete_many({"user_id": user_id})
                # Delete user's classifications
                await mongodb.db.classifications.delete_many({"user_id": user_id})
                return True
            except:
                await mongodb.db.users.delete_one({"id": user_id})
                await mongodb.db.conversations.delete_many({"user_id": user_id})
                await mongodb.db.classifications.delete_many({"user_id": user_id})
                return True
        else:
            # In-memory deletion
            mongodb._memory_store["users"] = [u for u in mongodb._memory_store.get("users", []) if u["id"] != user_id]
            mongodb._memory_store["conversations"] = {
                k: v for k, v in mongodb._memory_store.get("conversations", {}).items()
                if v.get("user_id") != user_id
            }
            mongodb._memory_store["classifications"] = [
                c for c in mongodb._memory_store.get("classifications", [])
                if c.get("user_id") != user_id
            ]
            return True
        return False


# Global auth service instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get or initialize global auth service."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
