"""
Conversations API endpoints for persisting and retrieving chat sessions.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from ..core.mongodb import get_mongodb

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_conversations(limit: int = Query(20, ge=1, le=100)):
    """List recent conversation sessions."""
    mongo = get_mongodb()
    return await mongo.list_conversations(limit=limit)

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Retrieve full message history for a specific conversation."""
    mongo = get_mongodb()
    conv = await mongo.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv
