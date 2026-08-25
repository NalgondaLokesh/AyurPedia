"""
MongoDB Cloud (Atlas) connection and persistence manager for AyurPedia.
Provides asynchronous and synchronous access with automated index management
and in-memory fallback if MongoDB is temporarily unconfigured.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo

logger = logging.getLogger(__name__)

class MongoDBManager:
    """Manager for MongoDB Cloud connections and collections."""
    
    def __init__(self, uri: str = "", db_name: str = "ayurpedia") -> None:
        self.uri = uri.strip()
        self.db_name = db_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.sync_client: Optional[pymongo.MongoClient] = None
        self.is_connected = False
        
        # In-memory storage fallback if MongoDB is not configured
        self._memory_store = {
            "conversations": {},
            "classifications": [],
            "facilitator_requests": [],
            "audit_logs": []
        }
    
    async def connect(self) -> bool:
        """Initialize connection to MongoDB Atlas."""
        if not self.uri or "your_mongodb_uri" in self.uri:
            logger.info("MongoDB URI not configured. Running with in-memory persistence.")
            return False
            
        try:
            self.client = AsyncIOMotorClient(
                self.uri,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=5
            )
            # Verify connection with ping
            await self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.is_connected = True
            logger.info(f"Connected to MongoDB Atlas: database='{self.db_name}'")
            
            # Setup indexes
            await self._ensure_indexes()
            return True
        except Exception as e:
            logger.warning(f"MongoDB connection failed ({e}). Falling back to in-memory store.")
            self.is_connected = False
            return False
            
    async def _ensure_indexes(self) -> None:
        """Ensure necessary indexes are created."""
        if not self.is_connected or self.db is None:
            return
        try:
            # Conversations index
            await self.db.conversations.create_index([("conversation_id", pymongo.ASCENDING)], unique=True)
            await self.db.conversations.create_index([("updated_at", pymongo.DESCENDING)])
            
            # Classifications index
            await self.db.classifications.create_index([("created_at", pymongo.DESCENDING)])
            
            # Facilitator requests index
            await self.db.facilitator_requests.create_index([("created_at", pymongo.DESCENDING)])
            
            logger.info("MongoDB indexes verified successfully.")
        except Exception as e:
            logger.warning(f"Failed to create MongoDB indexes: {e}")
            
    async def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("MongoDB connection closed.")

    # -------------------------------------------------------------
    # Chat & Conversation Persistence
    # -------------------------------------------------------------
    async def save_message(self, conversation_id: str, message: Dict[str, Any], jurisdiction: str = "India", language: str = "en") -> bool:
        """Save or append a message to a conversation."""
        now = datetime.utcnow().isoformat()
        if self.is_connected and self.db is not None:
            try:
                await self.db.conversations.update_one(
                    {"conversation_id": conversation_id},
                    {
                        "$setOnInsert": {
                            "created_at": now,
                            "jurisdiction": jurisdiction,
                            "language": language
                        },
                        "$set": {"updated_at": now},
                        "$push": {"messages": message}
                    },
                    upsert=True
                )
                return True
            except Exception as e:
                logger.error(f"Failed to save message to MongoDB: {e}")
        
        # In-memory fallback
        if conversation_id not in self._memory_store["conversations"]:
            self._memory_store["conversations"][conversation_id] = {
                "conversation_id": conversation_id,
                "created_at": now,
                "updated_at": now,
                "jurisdiction": jurisdiction,
                "language": language,
                "messages": []
            }
        self._memory_store["conversations"][conversation_id]["updated_at"] = now
        self._memory_store["conversations"][conversation_id]["messages"].append(message)
        return True

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full conversation document by ID."""
        if self.is_connected and self.db is not None:
            try:
                doc = await self.db.conversations.find_one({"conversation_id": conversation_id}, {"_id": 0})
                return doc
            except Exception as e:
                logger.error(f"Failed to fetch conversation from MongoDB: {e}")
        
        return self._memory_store["conversations"].get(conversation_id)

    async def list_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent conversation summaries."""
        if self.is_connected and self.db is not None:
            try:
                cursor = self.db.conversations.find(
                    {},
                    {"_id": 0, "conversation_id": 1, "created_at": 1, "updated_at": 1, "jurisdiction": 1, "language": 1, "messages": {"$slice": -1}}
                ).sort("updated_at", -1).limit(limit)
                return await cursor.to_list(length=limit)
            except Exception as e:
                logger.error(f"Failed to list conversations from MongoDB: {e}")
        
        convs = list(self._memory_store["conversations"].values())
        convs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return convs[:limit]

    # -------------------------------------------------------------
    # Formulation Classification Persistence
    # -------------------------------------------------------------
    async def save_classification(self, classification_data: Dict[str, Any]) -> str:
        """Save a completed formulation classification result."""
        now = datetime.utcnow().isoformat()
        classification_data["created_at"] = now
        
        if self.is_connected and self.db is not None:
            try:
                result = await self.db.classifications.insert_one(classification_data)
                return str(result.inserted_id)
            except Exception as e:
                logger.error(f"Failed to save classification to MongoDB: {e}")
                
        self._memory_store["classifications"].append(classification_data)
        return "mem_" + str(len(self._memory_store["classifications"]))

    async def list_classifications(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent classification records."""
        if self.is_connected and self.db is not None:
            try:
                cursor = self.db.classifications.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
                return await cursor.to_list(length=limit)
            except Exception as e:
                logger.error(f"Failed to list classifications: {e}")
                
        return sorted(self._memory_store["classifications"], key=lambda x: x.get("created_at", ""), reverse=True)[:limit]

    # -------------------------------------------------------------
    # Facilitator Escalation Persistence
    # -------------------------------------------------------------
    async def save_facilitator_request(self, request_data: Dict[str, Any]) -> str:
        """Save human facilitator escalation request."""
        now = datetime.utcnow().isoformat()
        request_data["created_at"] = now
        request_data["status"] = request_data.get("status", "Pending")
        
        if self.is_connected and self.db is not None:
            try:
                result = await self.db.facilitator_requests.insert_one(request_data)
                return str(result.inserted_id)
            except Exception as e:
                logger.error(f"Failed to save facilitator request to MongoDB: {e}")
                
        self._memory_store["facilitator_requests"].append(request_data)
        return "mem_" + str(len(self._memory_store["facilitator_requests"]))


# Global MongoDB manager instance
_mongo_manager: Optional[MongoDBManager] = None

def get_mongodb() -> MongoDBManager:
    """Get or initialize global MongoDB manager."""
    global _mongo_manager
    if _mongo_manager is None:
        from .config import get_config
        cfg = get_config()
        _mongo_manager = MongoDBManager(uri=cfg.mongodb_uri, db_name=cfg.mongodb_db_name)
    return _mongo_manager
