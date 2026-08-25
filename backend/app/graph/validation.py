"""
Validation node module for AyurPedia.
Handles citation validation and confidence scoring.
"""

import logging
from typing import Dict, Any, List
from ..core.config import get_config
from ..models.document import DocumentChunk


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationNode:
    """Validation node for LangGraph workflow."""
    
    def __init__(self) -> None:
        """Initialize validation node."""
        logger.info("ValidationNode initialized")
    
    def validate(self, response: str, citations: List[Dict[str, str]], 
                 retrieved_docs: List[DocumentChunk], confidence: str) -> Dict[str, Any]:
        """Validate citations and confidence score.
        
        Args:
            response: Generated response
            citations: List of citations
            retrieved_docs: List of retrieved documents
            confidence: Current confidence level
            
        Returns:
            Dictionary with validation results
        """
        logger.info("Executing validation node")
        
        # Check if response has citations
        has_citations = len(citations) > 0
        
        # Check if citations match retrieved documents
        citations_valid = self._validate_citations_match(citations, retrieved_docs)
        
        # Check if confidence meets threshold
        config = get_config()
        confidence_map = {"High": 0.8, "Medium": 0.6, "Low": 0.4}
        confidence_score = confidence_map.get(confidence, 0.5)
        confidence_valid = confidence_score >= config.confidence_threshold
        
        # Determine overall validity
        if not has_citations:
            logger.warning("Response has no citations")
            return {
                "valid": False,
                "confidence": "Low",
                "reason": "Response lacks citations",
                "should_abstain": True
            }
        
        if not citations_valid:
            logger.warning("Citations do not match retrieved documents")
            return {
                "valid": False,
                "confidence": "Low",
                "reason": "Citations do not match retrieved documents",
                "should_abstain": True
            }
        
        if not confidence_valid:
            logger.warning(f"Confidence {confidence} below threshold {config.confidence_threshold}")
            return {
                "valid": False,
                "confidence": "Low",
                "reason": f"Confidence below threshold ({config.confidence_threshold})",
                "should_abstain": True
            }
        
        # Check for partially uncited claims
        uncited_claims = self._check_uncited_claims(response, citations)
        if uncited_claims:
            logger.warning(f"Found {len(uncited_claims)} potentially uncited claims")
            return {
                "valid": True,
                "confidence": confidence,
                "reason": f"Response has citations but {len(uncited_claims)} claims may be uncited",
                "should_abstain": False,
                "warning": f"{len(uncited_claims)} claims may lack citations"
            }
        
        logger.info("Validation passed")
        return {
            "valid": True,
            "confidence": confidence,
            "reason": "Response is properly cited and confident",
            "should_abstain": False
        }
    
    def _validate_citations_match(self, citations: List[Dict[str, str]], 
                                 retrieved_docs: List[DocumentChunk]) -> bool:
        """Check if citations match retrieved documents.
        
        Args:
            citations: List of citations
            retrieved_docs: List of retrieved documents
            
        Returns:
            True if citations match documents
        """
        if not citations:
            return False
        
        # Create set of valid sources and sections from retrieved docs
        valid_sources = set()
        valid_sections = set()
        
        for doc in retrieved_docs:
            metadata = doc.metadata
            source = metadata.get('source', '').lower()
            section = metadata.get('section', '').lower()
            if source:
                valid_sources.add(source)
            if section:
                valid_sections.add(section)
        
        # Check each citation
        for citation in citations:
            source = citation.get('source', '').lower()
            section = citation.get('section', '').lower()
            
            # Citation must match either source or section
            if source not in valid_sources and section not in valid_sections:
                return False
        
        return True
    
    def _check_uncited_claims(self, response: str, citations: List[Dict[str, str]]) -> List[str]:
        """Check for potentially uncited claims in response.
        
        Args:
            response: Generated response
            citations: List of citations
            
        Returns:
            List of potentially uncited claims
        """
        # This is a simple heuristic - in production, use more sophisticated NLP
        uncited_claims = []
        
        # Split response into sentences
        sentences = response.split('.')
        
        # Count citations
        num_citations = len(citations)
        num_sentences = len([s for s in sentences if s.strip()])
        
        # If there are significantly more sentences than citations, flag potential uncited claims
        if num_sentences > num_citations * 2:
            uncited_claims.append(f"Response has {num_sentences} sentences but only {num_citations} citations")
        
        return uncited_claims
