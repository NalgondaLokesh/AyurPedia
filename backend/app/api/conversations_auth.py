"""
Conversation management API endpoints with user authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId

from ..core.mongodb import get_mongodb
from ..api.auth import get_current_user
from ..models.user import UserResponse

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class ConversationCreate(BaseModel):
    """Conversation creation model."""
    title: Optional[str] = None
    jurisdiction: str = "India"
    language: str = "en"


class ConversationResponse(BaseModel):
    """Conversation response model."""
    conversation_id: str
    user_id: str
    title: Optional[str]
    jurisdiction: str
    language: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class MessageCreate(BaseModel):
    """Message creation model."""
    sender: str
    text: str
    citations: Optional[List[dict]] = None
    confidence: Optional[float] = None
    jurisdiction: Optional[str] = None


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conv_data: ConversationCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new conversation for the authenticated user."""
    mongodb = get_mongodb()
    
    conversation_id = f"conv_{current_user.id}_{datetime.utcnow().timestamp()}"
    conversation_doc = {
        "conversation_id": conversation_id,
        "user_id": current_user.id,
        "title": conv_data.title or "New Conversation",
        "jurisdiction": conv_data.jurisdiction,
        "language": conv_data.language,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "messages": []
    }
    
    if mongodb.is_connected and mongodb.db is not None:
        await mongodb.db.conversations.insert_one(conversation_doc)
    else:
        if "conversations" not in mongodb._memory_store:
            mongodb._memory_store["conversations"] = {}
        mongodb._memory_store["conversations"][conversation_id] = conversation_doc
    
    return ConversationResponse(
        conversation_id=conversation_id,
        user_id=current_user.id,
        title=conversation_doc["title"],
        jurisdiction=conversation_doc["jurisdiction"],
        language=conversation_doc["language"],
        created_at=conversation_doc["created_at"],
        updated_at=conversation_doc["updated_at"],
        message_count=0
    )


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = 20,
    current_user: UserResponse = Depends(get_current_user)
):
    """List all conversations for the authenticated user."""
    mongodb = get_mongodb()
    conversations = []
    
    if mongodb.is_connected and mongodb.db is not None:
        cursor = mongodb.db.conversations.find(
            {"user_id": current_user.id}
        ).sort("updated_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            conversations.append(ConversationResponse(
                conversation_id=doc["conversation_id"],
                user_id=doc["user_id"],
                title=doc.get("title"),
                jurisdiction=doc["jurisdiction"],
                language=doc["language"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                message_count=len(doc.get("messages", []))
            ))
    else:
        for conv in mongodb._memory_store.get("conversations", {}).values():
            if conv.get("user_id") == current_user.id:
                conversations.append(ConversationResponse(
                    conversation_id=conv["conversation_id"],
                    user_id=conv["user_id"],
                    title=conv.get("title"),
                    jurisdiction=conv["jurisdiction"],
                    language=conv["language"],
                    created_at=conv["created_at"],
                    updated_at=conv["updated_at"],
                    message_count=len(conv.get("messages", []))
                ))
    
    return sorted(conversations, key=lambda x: x.updated_at, reverse=True)[:limit]


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific conversation by ID."""
    mongodb = get_mongodb()
    conversation = None
    
    if mongodb.is_connected and mongodb.db is not None:
        conversation = await mongodb.db.conversations.find_one({
            "conversation_id": conversation_id,
            "user_id": current_user.id
        }, {"_id": 0})
    else:
        conversation = mongodb._memory_store.get("conversations", {}).get(conversation_id)
        if conversation and conversation.get("user_id") != current_user.id:
            conversation = None
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.post("/{conversation_id}/messages")
async def add_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Add a message to a conversation."""
    mongodb = get_mongodb()
    
    # Verify conversation ownership
    if mongodb.is_connected and mongodb.db is not None:
        conversation = await mongodb.db.conversations.find_one({
            "conversation_id": conversation_id,
            "user_id": current_user.id
        })
    else:
        conversation = mongodb._memory_store.get("conversations", {}).get(conversation_id)
        if conversation and conversation.get("user_id") != current_user.id:
            conversation = None
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    message_doc = {
        "sender": message.sender,
        "text": message.text,
        "citations": message.citations or [],
        "confidence": message.confidence,
        "jurisdiction": message.jurisdiction,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if mongodb.is_connected and mongodb.db is not None:
        await mongodb.db.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$push": {"messages": message_doc},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
    else:
        mongodb._memory_store["conversations"][conversation_id]["messages"].append(message_doc)
        mongodb._memory_store["conversations"][conversation_id]["updated_at"] = datetime.utcnow()
    
    return {"message": "Message added successfully"}


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a conversation."""
    mongodb = get_mongodb()
    
    if mongodb.is_connected and mongodb.db is not None:
        result = await mongodb.db.conversations.delete_one({
            "conversation_id": conversation_id,
            "user_id": current_user.id
        })
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        if conversation_id in mongodb._memory_store.get("conversations", {}):
            if mongodb._memory_store["conversations"][conversation_id].get("user_id") == current_user.id:
                del mongodb._memory_store["conversations"][conversation_id]
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    
    return {"message": "Conversation deleted successfully"}
