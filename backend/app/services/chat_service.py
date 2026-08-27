"""
Chat service module for AyurPedia.
Handles business logic for chat queries.
"""

import logging
from typing import Dict, Any, Optional
from ..rag.chains import RAGChain
from ..models.chat import ChatRequest, ChatResponse, Citation


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat queries."""
    
    def __init__(self, agentic_rag: Any) -> None:
        """Initialize chat service with agentic RAG.
        
        Args:
            agentic_rag: AgenticRAGWorkflow instance for graph-based retrieval
        """
        self.agentic_rag = agentic_rag
        logger.info("ChatService initialized with agentic RAG")
    
    def process_query(self, request: ChatRequest) -> ChatResponse:
        """Process a chat query.
        
        Args:
            request: ChatRequest with query and jurisdiction
            
        Returns:
            ChatResponse with generated answer and citations
        """
        logger.info(f"Processing query: '{request.query}' in jurisdiction: {request.jurisdiction}")
        
        try:
            # Use agentic RAG
            logger.info("Using agentic RAG with graph retrieval")
            result = self.agentic_rag.invoke(
                request.query, 
                request.jurisdiction, 
                getattr(request, 'language', 'en')
            )
            
            # Format response
            response = self.format_response(result, request)
            
            # Add disclaimer
            response = self.add_disclaimer(response)
            
            # Persist to MongoDB
            self.persist_conversation(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            return ChatResponse(
                response="I encountered an error while processing your request. Please try again.",
                citations=[],
                confidence="Low",
                jurisdiction=request.jurisdiction
            )

    def persist_conversation(self, request: ChatRequest, response: ChatResponse) -> None:
        """Persist user query and AI response to MongoDB."""
        conv_id = request.conversation_id
        if not conv_id:
            return
        try:
            import asyncio
            from datetime import datetime
            from ..core.mongodb import get_mongodb
            mongo = get_mongodb()
            
            user_msg = {
                "id": f"usr_{int(datetime.utcnow().timestamp()*1000)}",
                "sender": "user",
                "text": request.query,
                "timestamp": datetime.utcnow().isoformat()
            }
            assistant_msg = {
                "id": f"ast_{int(datetime.utcnow().timestamp()*1000)}",
                "sender": "assistant",
                "text": response.response,
                "citations": [c.model_dump() for c in response.citations],
                "confidence": response.confidence,
                "jurisdiction": response.jurisdiction,
                "disclaimer": response.disclaimer,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(mongo.save_message(conv_id, user_msg, request.jurisdiction, getattr(request, 'language', 'en')))
                loop.create_task(mongo.save_message(conv_id, assistant_msg, request.jurisdiction, getattr(request, 'language', 'en')))
            except RuntimeError:
                # If running outside async event loop
                asyncio.run(mongo.save_message(conv_id, user_msg, request.jurisdiction, getattr(request, 'language', 'en')))
                asyncio.run(mongo.save_message(conv_id, assistant_msg, request.jurisdiction, getattr(request, 'language', 'en')))
        except Exception as e:
            logger.warning(f"Failed to persist conversation: {e}")
    
    def format_response(self, rag_result: Dict[str, Any], request: ChatRequest) -> ChatResponse:
        """Format RAG result to ChatResponse.
        
        Args:
            rag_result: Result from RAG chain execution
            request: Original chat request
            
        Returns:
            Formatted ChatResponse
        """
        # Convert citations
        citations = []
        for citation in rag_result.get('citations', []):
            citations.append(Citation(
                text=citation.get('text', ''),
                source=citation.get('source', ''),
                section=citation.get('section', '')
            ))
        
        # Handle agentic RAG additional fields
        response = ChatResponse(
            response=rag_result.get('response', ''),
            citations=citations,
            confidence=rag_result.get('confidence', 'Low'),
            jurisdiction=request.jurisdiction
        )
        
        # Add reasoning if available (from agentic RAG)
        if rag_result.get('reasoning'):
            response.reasoning = rag_result['reasoning']
        
        # Add graph path if available
        if rag_result.get('graph_path'):
            response.graph_path = rag_result['graph_path']
        
        return response
    
    def add_disclaimer(self, response: ChatResponse) -> ChatResponse:
        """Add legal disclaimer to response.
        
        Args:
            response: ChatResponse to add disclaimer to
            
        Returns:
            ChatResponse with disclaimer
        """
        response.disclaimer = "This is information, not legal advice. Consult a qualified legal professional."
        return response
