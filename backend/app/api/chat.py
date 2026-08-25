"""
Chat endpoint for AyurPedia API.
Handles chat queries with RAG and citations.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from ..models.chat import ChatRequest, ChatResponse
from ..services.chat_service import ChatService


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


# Global service instance (will be initialized on startup)
chat_service: ChatService = None


def set_chat_service(service: ChatService) -> None:
    """Set the chat service instance.
    
    Args:
        service: ChatService instance
    """
    global chat_service
    chat_service = service


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat query with RAG and citations.
    
    Args:
        request: ChatRequest with query and jurisdiction
        
    Returns:
        ChatResponse with generated answer and citations
        
    Raises:
        HTTPException: If service is not initialized or processing fails
    """
    if chat_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service not initialized"
        )
    
    try:
        logger.info(f"Received chat request: '{request.query}'")
        response = chat_service.process_query(request)
        logger.info(f"Chat response generated with confidence: {response.confidence}")
        return response
        
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )
