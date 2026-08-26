"""
Audit logging service for DPDP compliance.
"""

import logging
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from ..core.mongodb import get_mongodb
from ..models.audit import AuditLogCreate, AuditLogResponse, AuditAction

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging and compliance tracking."""
    
    def __init__(self):
        self.mongodb = get_mongodb()
    
    async def create_log(self, log_data: AuditLogCreate) -> str:
        """Create an audit log entry."""
        mongodb = get_mongodb()
        log_doc = {
            "user_id": log_data.user_id,
            "action": log_data.action.value,
            "resource_type": log_data.resource_type,
            "resource_id": log_data.resource_id,
            "ip_address": log_data.ip_address,
            "user_agent": log_data.user_agent,
            "metadata": log_data.metadata or {},
            "timestamp": datetime.utcnow()
        }
        
        if mongodb.is_connected and mongodb.db is not None:
            result = await mongodb.db.audit_logs.insert_one(log_doc)
            return str(result.inserted_id)
        else:
            if "audit_logs" not in mongodb._memory_store:
                mongodb._memory_store["audit_logs"] = []
            mongodb._memory_store["audit_logs"].append(log_doc)
            return "mem_" + str(len(mongodb._memory_store["audit_logs"]))
    
    async def get_user_logs(self, user_id: str, limit: int = 100) -> List[AuditLogResponse]:
        """Get audit logs for a specific user."""
        mongodb = get_mongodb()
        logs = []
        
        if mongodb.is_connected and mongodb.db is not None:
            try:
                cursor = mongodb.db.audit_logs.find(
                    {"user_id": user_id}
                ).sort("timestamp", -1).limit(limit)
                docs = await cursor.to_list(length=limit)
                for doc in docs:
                    logs.append(AuditLogResponse(
                        id=str(doc.get("_id", "")),
                        user_id=doc["user_id"],
                        action=AuditAction(doc["action"]),
                        resource_type=doc.get("resource_type"),
                        resource_id=doc.get("resource_id"),
                        ip_address=doc.get("ip_address"),
                        user_agent=doc.get("user_agent"),
                        metadata=doc.get("metadata"),
                        timestamp=doc["timestamp"]
                    ))
            except Exception as e:
                logger.error(f"Failed to fetch user audit logs: {e}")
        else:
            for log in mongodb._memory_store.get("audit_logs", []):
                if log.get("user_id") == user_id:
                    logs.append(AuditLogResponse(
                        id=log.get("id", ""),
                        user_id=log["user_id"],
                        action=AuditAction(log["action"]),
                        resource_type=log.get("resource_type"),
                        resource_id=log.get("resource_id"),
                        ip_address=log.get("ip_address"),
                        user_agent=log.get("user_agent"),
                        metadata=log.get("metadata"),
                        timestamp=log["timestamp"]
                    ))
        
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    async def get_logs_by_action(self, action: AuditAction, limit: int = 100) -> List[AuditLogResponse]:
        """Get audit logs by action type."""
        mongodb = get_mongodb()
        logs = []
        
        if mongodb.is_connected and mongodb.db is not None:
            cursor = mongodb.db.audit_logs.find(
                {"action": action.value}
            ).sort("timestamp", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
            for doc in docs:
                logs.append(AuditLogResponse(
                    id=str(doc.get("_id", "")),
                    user_id=doc["user_id"],
                    action=AuditAction(doc["action"]),
                    resource_type=doc.get("resource_type"),
                    resource_id=doc.get("resource_id"),
                    ip_address=doc.get("ip_address"),
                    user_agent=doc.get("user_agent"),
                    metadata=doc.get("metadata"),
                    timestamp=doc["timestamp"]
                ))
        else:
            for log in mongodb._memory_store.get("audit_logs", []):
                if log.get("action") == action.value:
                    logs.append(AuditLogResponse(
                        id=log.get("id", ""),
                        user_id=log["user_id"],
                        action=AuditAction(log["action"]),
                        resource_type=log.get("resource_type"),
                        resource_id=log.get("resource_id"),
                        ip_address=log.get("ip_address"),
                        user_agent=log.get("user_agent"),
                        metadata=log.get("metadata"),
                        timestamp=log["timestamp"]
                    ))
        
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]


# Global audit service instance
_audit_service: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    """Get or initialize global audit service."""
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service
