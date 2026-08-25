"""
Routing node module for AyurPedia.
Handles jurisdiction determination and workflow routing.
"""

import logging
from typing import Dict, Any


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RoutingNode:
    """Routing node for LangGraph workflow."""
    
    def __init__(self) -> None:
        """Initialize routing node."""
        # Classification to jurisdiction mapping
        self.classification_jurisdiction_map = {
            "Classical": "India",
            "Proprietary": "India",
            "Ayurveda-Aahar": "India",
            "Cosmetic": "India",
            "Phytopharmaceutical": "India",
            "Nutraceutical": "India",
            "Unknown": "India"
        }
        
        # Classification to relevant laws mapping
        self.classification_laws_map = {
            "Classical": ["Patents Act 1970", "FSSAI Ayurveda Aahar Regulations 2022"],
            "Proprietary": ["Patents Act 1970", "Biological Diversity Act 2002", "FSSAI Ayurveda Aahar Regulations 2022"],
            "Ayurveda-Aahar": ["FSSAI Ayurveda Aahar Regulations 2022", "Patents Act 1970"],
            "Cosmetic": ["Drugs and Cosmetics Act"],
            "Phytopharmaceutical": ["Patents Act 1970", "Biological Diversity Act 2002"],
            "Nutraceutical": ["FSSAI Ayurveda Aahar Regulations 2022"],
            "Unknown": []
        }
        
        logger.info("RoutingNode initialized")
    
    def route(self, query: str, classification: str, jurisdiction: str = "India") -> Dict[str, Any]:
        """Determine jurisdiction and workflow path based on classification.
        
        Args:
            query: User query
            classification: Classification result
            jurisdiction: User-specified jurisdiction (optional)
            
        Returns:
            Dictionary with routing decision
        """
        logger.info(f"Routing query with classification: {classification}")
        
        # If jurisdiction is explicitly provided by user, use it
        if jurisdiction and jurisdiction.lower() in ["india", "international", "both"]:
            logger.info(f"Using user-specified jurisdiction: {jurisdiction}")
            return {
                "jurisdiction": jurisdiction,
                "relevant_laws": self.classification_laws_map.get(classification, []),
                "search_collections": self._get_collections_for_jurisdiction(jurisdiction)
            }
        
        # Otherwise, determine jurisdiction from classification
        determined_jurisdiction = self.classification_jurisdiction_map.get(
            classification, "India"
        )
        
        logger.info(f"Determined jurisdiction: {determined_jurisdiction}")
        
        return {
            "jurisdiction": determined_jurisdiction,
            "relevant_laws": self.classification_laws_map.get(classification, []),
            "search_collections": self._get_collections_for_jurisdiction(determined_jurisdiction)
        }
    
    def _get_collections_for_jurisdiction(self, jurisdiction: str) -> list:
        """Get Qdrant collections to search based on jurisdiction.
        
        Args:
            jurisdiction: Jurisdiction (India, International, or Both)
            
        Returns:
            List of collection names to search
        """
        from ..core.config import get_config
        config = get_config()
        
        if jurisdiction.lower() == "india":
            return [config.india_collection]
        elif jurisdiction.lower() == "international":
            return [config.international_collection]
        elif jurisdiction.lower() == "both":
            return [config.india_collection, config.international_collection]
        else:
            logger.warning(f"Unknown jurisdiction: {jurisdiction}, defaulting to India")
            return [config.india_collection]
    
    def should_search_international(self, query: str) -> bool:
        """Determine if query requires international law search.
        
        Args:
            query: User query
            
        Returns:
            True if international search is needed
        """
        international_keywords = [
            "wipo", "gratk", "trips", "nagoya", "protocol",
            "international", "treaty", "convention", "patent cooperation treaty",
            "pct", "wipo", "world intellectual property"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in international_keywords)
    
    def should_search_india(self, query: str) -> bool:
        """Determine if query requires Indian law search.
        
        Args:
            query: User query
            
        Returns:
            True if India search is needed
        """
        india_keywords = [
            "india", "indian", "patents act", "biological diversity",
            "fssai", "ayurveda", "traditional knowledge", "genetic resources",
            "drugs and cosmetics", "phytopharmaceutical", "nutraceutical"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in india_keywords)
