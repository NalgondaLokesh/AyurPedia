"""
User-related Pydantic models for AyurPedia.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    full_name: Optional[str] = None
    organization: Optional[str] = None


class UserCreate(UserBase):
    """User registration model."""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class UserInDB(UserBase):
    """User model as stored in database."""
    id: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    consent_given: bool = False
    privacy_settings: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User response model (without sensitive data)."""
    id: str
    is_active: bool
    created_at: datetime
    consent_given: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token data model."""
    user_id: Optional[str] = None
    email: Optional[str] = None


class ConsentUpdate(BaseModel):
    """Consent update model."""
    consent_given: bool
    consent_date: Optional[datetime] = None


class PrivacySettings(BaseModel):
    """Privacy settings model."""
    data_retention_days: int = 90
    allow_analytics: bool = False
    allow_marketing: bool = False
    conversation_history_enabled: bool = True
