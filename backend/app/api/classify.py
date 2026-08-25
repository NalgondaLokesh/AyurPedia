"""
Classification endpoint for AyurPedia API.
Handles formulation classification.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from ..models.classification import ClassificationRequest, ClassificationResponse
from ..services.classification_service import ClassificationService


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/classify", tags=["classification"])


# Global service instance (will be initialized on startup)
classification_service: ClassificationService = None


def set_classification_service(service: ClassificationService) -> None:
    """Set the classification service instance.
    
    Args:
        service: ClassificationService instance
    """
    global classification_service
    classification_service = service


@router.post("", response_model=ClassificationResponse, status_code=status.HTTP_200_OK)
async def classify(request: ClassificationRequest) -> ClassificationResponse:
    """Classify a formulation description.
    
    Args:
        request: ClassificationRequest with formulation description
        
    Returns:
        ClassificationResponse with category and relevant laws
        
    Raises:
        HTTPException: If service is not initialized or processing fails
    """
    if classification_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Classification service not initialized"
        )
    
    try:
        logger.info(f"Received classification request: '{request.formulation_description[:100]}...'")
        response = classification_service.classify(request)
        logger.info(f"Classification result: {response.category} (confidence: {response.confidence})")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Classification request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to classify formulation: {str(e)}"
        )
