"""
Conversations API endpoints for persisting and retrieving chat sessions.
"""

import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from ..core.mongodb import get_mongodb
from ..api.auth import get_current_user
from ..models.user import UserResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_conversations(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user)
):
    """List recent conversation sessions for the authenticated user."""
    mongo = get_mongodb()
    return await mongo.list_conversations(limit=limit, user_id=current_user.id)

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Retrieve full message history for a specific conversation."""
    mongo = get_mongodb()
    conv = await mongo.get_conversation(conversation_id, user_id=current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.post("")
async def create_conversation(
    jurisdiction: str = "India",
    language: str = "en",
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new conversation session."""
    from datetime import datetime
    import uuid
    mongo = get_mongodb()
    
    conversation_id = str(uuid.uuid4())
    conversation_doc = {
        "conversation_id": conversation_id,
        "user_id": current_user.id,
        "title": "New conversation",
        "jurisdiction": jurisdiction,
        "language": language,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "messages": []
    }
    
    if mongo.is_connected and mongo.db is not None:
        await mongo.db.conversations.insert_one(conversation_doc)
    else:
        if "conversations" not in mongo._memory_store:
            mongo._memory_store["conversations"] = {}
        mongo._memory_store["conversations"][conversation_id] = conversation_doc
    
    return {"conversation_id": conversation_id}

@router.post("/{conversation_id}/messages")
async def add_message(
    conversation_id: str,
    message: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user)
):
    """Add a message to a conversation."""
    from datetime import datetime
    mongo = get_mongodb()
    
    # Verify conversation exists and belongs to user
    conv = await mongo.get_conversation(conversation_id, user_id=current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Add message to conversation
    message_doc = {
        **message,
        "created_at": datetime.utcnow()
    }
    
    if mongo.is_connected and mongo.db is not None:
        await mongo.db.conversations.update_one(
            {"conversation_id": conversation_id, "user_id": current_user.id},
            {
                "$push": {"messages": message_doc},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
    else:
        if "conversations" not in mongo._memory_store:
            mongo._memory_store["conversations"] = {}
        if conversation_id in mongo._memory_store["conversations"]:
            mongo._memory_store["conversations"][conversation_id]["messages"].append(message_doc)
            mongo._memory_store["conversations"][conversation_id]["updated_at"] = datetime.utcnow()
    
    return {"status": "success"}

@router.delete("/{conversation_id}/messages/{message_id}")
async def delete_message(
    conversation_id: str,
    message_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a specific message and its paired message from a conversation."""
    from datetime import datetime
    mongo = get_mongodb()
    
    logger.info(f"Delete request: conversation_id={conversation_id}, message_id={message_id}")
    
    # Verify conversation exists and belongs to user
    conv = await mongo.get_conversation(conversation_id, user_id=current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    logger.info(f"Conversation found with {len(conv.get('messages', []))} messages")
    
    # Delete message by id field
    if mongo.is_connected and mongo.db is not None:
        # First, find the message to determine its pairing
        conv_doc = await mongo.db.conversations.find_one(
            {"conversation_id": conversation_id, "user_id": current_user.id}
        )
        
        if not conv_doc or "messages" not in conv_doc:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = conv_doc["messages"]
        logger.info(f"Messages in DB: {len(messages)}")
        
        # Log first few message IDs for debugging
        for i, msg in enumerate(messages[:5]):
            logger.info(f"Message {i}: id={msg.get('id')}, sender={msg.get('sender')}")
        
        # Find the message (check both 'id' and '_id' fields for compatibility)
        message_to_delete = None
        for msg in messages:
            if msg.get("id") == message_id or msg.get("_id") == message_id:
                message_to_delete = msg
                break
        
        if not message_to_delete:
            raise HTTPException(status_code=404, detail=f"Message not found with id: {message_id}")
        
        # Determine which messages to delete using explicit association (new) or array position (old)
        ids_to_delete = [message_id]
        
        # New logic: use parent_message_id if available
        if message_to_delete.get("parent_message_id") or any(msg.get("parent_message_id") for msg in messages):
            # If deleting user message, find assistant message with parent_message_id
            if message_to_delete.get("sender") == "user":
                for msg in messages:
                    if msg.get("parent_message_id") == message_id:
                        ids_to_delete.append(msg.get("id"))
                        logger.info(f"Will also delete assistant message: {msg.get('id')}")
                        break
            # If deleting assistant message, find the user message it references
            elif message_to_delete.get("sender") == "assistant":
                parent_id = message_to_delete.get("parent_message_id")
                if parent_id:
                    ids_to_delete.append(parent_id)
                    logger.info(f"Will also delete user message: {parent_id}")
        else:
            # Fallback: old array-position logic for backward compatibility
            msg_index = messages.index(message_to_delete)
            logger.info(f"Using old array-position logic for message at index {msg_index}")
            
            if message_to_delete.get("sender") == "user" and msg_index + 1 < len(messages):
                next_msg = messages[msg_index + 1]
                if next_msg.get("sender") == "assistant":
                    next_id = next_msg.get("id") or next_msg.get("_id")
                    if next_id:
                        ids_to_delete.append(next_id)
                        logger.info(f"Will also delete assistant message (old logic): {next_id}")
            elif message_to_delete.get("sender") == "assistant" and msg_index > 0:
                prev_msg = messages[msg_index - 1]
                if prev_msg.get("sender") == "user":
                    prev_id = prev_msg.get("id") or prev_msg.get("_id")
                    if prev_id:
                        ids_to_delete.append(prev_id)
                        logger.info(f"Will also delete user message (old logic): {prev_id}")
        
        # Delete all messages by pulling them from the array
        for id_to_delete in ids_to_delete:
            result = await mongo.db.conversations.update_one(
                {"conversation_id": conversation_id, "user_id": current_user.id},
                {
                    "$pull": {"messages": {"id": id_to_delete}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            logger.info(f"Delete result for {id_to_delete}: matched={result.matched_count}, modified={result.modified_count}")
        
        return {"status": "success", "deleted_count": len(ids_to_delete)}
    else:
        # In-memory fallback
        if "conversations" not in mongo._memory_store:
            mongo._memory_store["conversations"] = {}
        if conversation_id in mongo._memory_store["conversations"]:
            messages = mongo._memory_store["conversations"][conversation_id]["messages"]
            
            message_to_delete = None
            for msg in messages:
                if msg.get("id") == message_id:
                    message_to_delete = msg
                    break
            
            if not message_to_delete:
                raise HTTPException(status_code=404, detail="Message not found")
            
            ids_to_delete = [message_id]
            
            # If deleting user message, find assistant message with parent_message_id
            if message_to_delete.get("sender") == "user":
                for msg in messages:
                    if msg.get("parent_message_id") == message_id:
                        ids_to_delete.append(msg.get("id"))
                        break
            # If deleting assistant message, find the user message it references
            elif message_to_delete.get("sender") == "assistant":
                parent_id = message_to_delete.get("parent_message_id")
                if parent_id:
                    ids_to_delete.append(parent_id)
            
            # Filter out deleted messages
            mongo._memory_store["conversations"][conversation_id]["messages"] = [
                msg for msg in messages if msg.get("id") not in ids_to_delete
            ]
            mongo._memory_store["conversations"][conversation_id]["updated_at"] = datetime.utcnow()
            return {"status": "success", "deleted_count": len(ids_to_delete)}
        
        raise HTTPException(status_code=404, detail="Conversation not found")
