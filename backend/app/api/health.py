"""
Health check endpoint for AyurPedia API.
Handles service health monitoring.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from ..core.database import QdrantDB
from ..core.llm import get_llm_client
from ..core.config import get_config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("", status_code=status.HTTP_200_OK)
async def health_check() -> dict:
    """Check health status of all services.
    
    Returns:
        Dictionary with service status information
    """
    try:
        config = get_config()
        llm_client = get_llm_client()
        
        # Check Qdrant connection
        qdrant_status = _check_qdrant(config)
        
        # Check Gemini API availability
        gemini_status = _check_gemini(llm_client)
        
        # Check NVIDIA NIM availability
        nvidia_status = _check_nvidia(llm_client)
        
        # Overall status
        overall_status = "healthy" if all([
            qdrant_status["status"] == "ok",
            gemini_status["status"] == "ok" or nvidia_status["status"] == "ok"
        ]) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "qdrant": qdrant_status,
                "gemini_llm": gemini_status,
                "nvidia_nim": nvidia_status,
                "embedding": {
                    "status": "ok" if llm_client.get_embedding_model() else "error",
                    "message": "Cohere embedding model" if llm_client.get_embedding_model() else "Embedding model not available"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


def _check_qdrant(config) -> dict:
    """Check Qdrant connection.
    
    Args:
        config: Configuration instance
        
    Returns:
        Dictionary with Qdrant status
    """
    try:
        qdrant_db = QdrantDB(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
            embedding_dimension=config.embedding_dimension
        )
        
        # Try to get collection info
        india_info = qdrant_db.get_collection_info(config.india_collection)
        international_info = qdrant_db.get_collection_info(config.international_collection)
        
        return {
            "status": "ok",
            "message": "Qdrant connected",
            "collections": {
                "india": india_info["points_count"] if india_info else 0,
                "international": international_info["points_count"] if international_info else 0
            }
        }
    except Exception as e:
        logger.warning(f"Qdrant health check failed: {e}")
        return {
            "status": "error",
            "message": f"Qdrant connection failed: {str(e)}"
        }


def _check_gemini(llm_client) -> dict:
    """Check Gemini API availability.
    
    Args:
        llm_client: LLM client instance
        
    Returns:
        Dictionary with Gemini status
    """
    try:
        is_available = llm_client.is_primary_available()
        if is_available:
            return {
                "status": "ok",
                "message": "Gemini API available"
            }
        else:
            return {
                "status": "error",
                "message": "Gemini API not available"
            }
    except Exception as e:
        logger.warning(f"Gemini health check failed: {e}")
        return {
            "status": "error",
            "message": f"Gemini health check failed: {str(e)}"
        }


def _check_nvidia(llm_client) -> dict:
    """Check NVIDIA NIM availability.
    
    Args:
        llm_client: LLM client instance
        
    Returns:
        Dictionary with NVIDIA NIM status
    """
    try:
        status = llm_client.get_status()
        if status["fallback_available"]:
            return {
                "status": "ok",
                "message": f"NVIDIA NIM available ({status['fallback_model']})"
            }
        else:
            return {
                "status": "error",
                "message": "NVIDIA NIM not available"
            }
    except Exception as e:
        logger.warning(f"NVIDIA NIM health check failed: {e}")
        return {
            "status": "error",
            "message": f"NVIDIA NIM health check failed: {str(e)}"
        }
