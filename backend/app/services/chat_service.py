"""
Chat service module for AyurPedia.
Handles business logic for chat queries.
"""

import logging
import re
from typing import Dict, Any, Optional
from ..rag.chains import RAGChain
from ..models.chat import ChatRequest, ChatResponse, Citation


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Jurisdiction-specific keywords
INDIA_KEYWORDS = [
    'section 3(p)', 'section 3p', 'patents act 1970', 'indian patents act',
    'national biodiversity authority', 'nba', 'biological diversity act 2002',
    'fssai', 'ayurveda-aahar', 'ayurveda aahar', 'food safety',
    'tkdl', 'traditional knowledge digital library',
    'indian patent office', 'indian ipr',
    'drugs and cosmetics act', 'ayurvedic pharmacopoeia'
]

INTERNATIONAL_KEYWORDS = [
    'wipo gratk', 'gratk treaty', 'wipo treaty',
    'nagoya protocol', 'access and benefit-sharing', 'abs',
    'trips agreement', 'trips', 'wto',
    'genetic resources', 'traditional knowledge',
    'international treaty', 'united nations',
    'cbd', 'convention on biological diversity',
    'patent cooperation treaty', 'pct'
]


def detect_jurisdiction_mismatch(query: str, selected_jurisdiction: str) -> Optional[str]:
    """Detect if query belongs to a different jurisdiction than selected.
    
    Args:
        query: User query text
        selected_jurisdiction: Selected jurisdiction (India, International, Both)
        
    Returns:
        Error message if mismatch detected, None otherwise
    """
    if selected_jurisdiction == 'Both':
        return None  # Both allows any query
    
    query_lower = query.lower()
    
    if selected_jurisdiction == 'India':
        # Check for international keywords
        for keyword in INTERNATIONAL_KEYWORDS:
            if keyword in query_lower:
                return f"This query appears to be about international frameworks ({keyword}). Please switch to the 'International' jurisdiction or use 'Both' to search across all frameworks."
    
    elif selected_jurisdiction == 'International':
        # Check for India-specific keywords
        for keyword in INDIA_KEYWORDS:
            if keyword in query_lower:
                return f"This query appears to be about Indian regulations ({keyword}). Please switch to the 'India' jurisdiction or use 'Both' to search across all frameworks."
    
    return None


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
        
        # Check for jurisdiction mismatch
        mismatch_error = detect_jurisdiction_mismatch(request.query, request.jurisdiction)
        if mismatch_error:
            logger.warning(f"Jurisdiction mismatch detected: {mismatch_error}")
            return ChatResponse(
                response=mismatch_error,
                citations=[],
                confidence="Low",
                jurisdiction=request.jurisdiction
            )
        
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
        user_id = getattr(request, 'user_id', None)
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
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
            assistant_msg = {
                "id": f"ast_{int(datetime.utcnow().timestamp()*1000)}",
                "sender": "assistant",
                "text": response.response,
                "citations": [c.model_dump() for c in response.citations],
                "confidence": response.confidence,
                "jurisdiction": response.jurisdiction,
                "disclaimer": response.disclaimer,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
            
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(mongo.save_message(conv_id, user_msg, request.jurisdiction, getattr(request, 'language', 'en'), user_id))
                loop.create_task(mongo.save_message(conv_id, assistant_msg, request.jurisdiction, getattr(request, 'language', 'en'), user_id))
            except RuntimeError:
                # If running outside async event loop
                asyncio.run(mongo.save_message(conv_id, user_msg, request.jurisdiction, getattr(request, 'language', 'en'), user_id))
                asyncio.run(mongo.save_message(conv_id, assistant_msg, request.jurisdiction, getattr(request, 'language', 'en'), user_id))
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
        
        # Calculate numeric confidence score from confidence level
        confidence_level = rag_result.get('confidence', 'Low')
        confidence_score = None
        if confidence_level == 'High':
            confidence_score = 0.85
        elif confidence_level == 'Medium':
            confidence_score = 0.60
        elif confidence_level == 'Low':
            confidence_score = 0.35
        
        # Handle agentic RAG additional fields
        response = ChatResponse(
            response=rag_result.get('response', ''),
            citations=citations,
            confidence=confidence_level,
            confidence_score=confidence_score,
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
