"""
Audit log models for AyurPedia DPDP compliance.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AuditAction(str, Enum):
    """Audit action types."""
    USER_REGISTER = "user_register"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    CONVERSATION_CREATE = "conversation_create"
    CONVERSATION_DELETE = "conversation_delete"
    CLASSIFICATION_CREATE = "classification_create"
    CONSENT_UPDATE = "consent_update"
    DATA_EXPORT = "data_export"
    DATA_DELETE = "data_delete"
    PRIVACY_SETTINGS_UPDATE = "privacy_settings_update"
    API_ACCESS = "api_access"


class AuditLogCreate(BaseModel):
    """Audit log creation model."""
    user_id: str
    action: AuditAction
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AuditLogResponse(BaseModel):
    """Audit log response model."""
    id: str
    user_id: str
    action: AuditAction
    resource_type: Optional[str]
    resource_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: Optional[Dict[str, Any]]
    timestamp: datetime
    
    class Config:
        from_attributes = True
