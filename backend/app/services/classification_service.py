"""
Classification service module for AyurPedia.
Handles business logic for formulation classification.
"""

import logging
from typing import Dict, Any
from ..graph.workflow import GraphWorkflow
from ..graph.classification import ClassificationNode
from ..models.classification import ClassificationRequest, ClassificationResponse


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClassificationService:
    """Service for handling formulation classification."""
    
    def __init__(self, workflow: GraphWorkflow) -> None:
        """Initialize classification service with workflow.
        
        Args:
            workflow: LangGraph workflow instance
        """
        self.workflow = workflow
        self.classification_node = ClassificationNode(workflow.llm)
        logger.info("ClassificationService initialized")
    
    def classify(self, request: ClassificationRequest) -> ClassificationResponse:
        """Classify a formulation description.
        
        Args:
            request: ClassificationRequest with formulation description
            
        Returns:
            ClassificationResponse with category and relevant laws
        """
        logger.info(f"Classifying formulation: '{request.formulation_description[:100]}...'")
        
        try:
            # Validate input
            self.validate_input(request.formulation_description)
            
            # Perform classification
            classification_result = self.classification_node.classify(
                request.formulation_description
            )
            
            # Format response
            response = self.format_classification(classification_result)
            
            # Log interaction
            self.log_interaction(request, response)
            
            return response
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return ClassificationResponse(
                category="Unknown",
                confidence=0.0,
                relevant_laws=[],
                description=f"Invalid input: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return ClassificationResponse(
                category="Unknown",
                confidence=0.0,
                relevant_laws=[],
                description="Classification failed due to an error"
            )
    
    def format_classification(self, result: Dict[str, Any]) -> ClassificationResponse:
        """Format classification result to ClassificationResponse.
        
        Args:
            result: Classification result from node
            
        Returns:
            Formatted ClassificationResponse
        """
        # Determine jurisdiction from category
        jurisdiction = self.classification_node.map_to_jurisdiction(result['category'])
        
        return ClassificationResponse(
            category=result['category'],
            confidence=result['confidence'],
            relevant_laws=result['relevant_laws'],
            description=result['description'],
            jurisdiction=jurisdiction
        )
    
    def validate_input(self, description: str) -> None:
        """Validate formulation description input.
        
        Args:
            description: Formulation description to validate
            
        Raises:
            ValueError: If validation fails
        """
        if not description or not description.strip():
            raise ValueError("Formulation description cannot be empty")
        
        if len(description) < 10:
            raise ValueError("Formulation description must be at least 10 characters")
        
        if len(description) > 2000:
            raise ValueError("Formulation description must not exceed 2000 characters")
    
    def log_interaction(self, request: ClassificationRequest, response: ClassificationResponse) -> None:
        """Log classification interaction for audit purposes.
        
        Args:
            request: ClassificationRequest
            response: ClassificationResponse
        """
        try:
            from ..utils.logging import log_interaction
            log_interaction(
                user_id=None,
                query=request.formulation_description,
                jurisdiction=response.jurisdiction,
                response=response.description,
                citations=response.relevant_laws,
                confidence=str(response.confidence)
            )
        except Exception as e:
            logger.warning(f"Failed to log interaction: {e}")
